
"""Audio playback & synthesis utilities for FastAPI backends.

This module provides:
  - `AudioPlayer` class: synthesize notes (WAV bytes) with simple ADSR.
  - FastAPI router (optional): endpoints to list/stream audio files and synthesize notes.

How to wire into your FastAPI app (no other file changes required besides import):
    from audio_player import router as audio_router
    app.include_router(audio_router)  # exposes /audio/... endpoints

Minimal example to generate a note in code:
    from audio_player import AudioPlayer
    ap = AudioPlayer()
    wav_bytes = ap.synthesize_note(note="A", octave=4, duration=1.0)
    with open("A4.wav", "wb") as f:
        f.write(wav_bytes)

Folder conventions:
  - Static audio files served via streaming are looked up under ./static/audio
    (create it if it doesn't exist). Only files within this directory are accessible.
"""

from __future__ import annotations

import io
import math
import os
import wave
import struct
from pathlib import Path
from typing import Generator, Iterable, List, Optional, Tuple

try:
    # Optional: Only imported if FastAPI is available
    from fastapi import APIRouter, HTTPException, Query, Request
    from fastapi.responses import Response, StreamingResponse, JSONResponse
except Exception:  # pragma: no cover - allows using the class without FastAPI installed
    APIRouter = None  # type: ignore
    HTTPException = Exception  # type: ignore
    Request = object  # type: ignore
    Response = object  # type: ignore
    StreamingResponse = object  # type: ignore
    JSONResponse = object  # type: ignore

__all__ = ["AudioPlayer", "router"]

# ---------------------------
# Core synthesis engine
# ---------------------------

class AudioPlayer:
    """Tiny audio synthesis helper (no external deps).

    Generates mono 16-bit PCM WAV bytes for single tones/notes with a simple ADSR.
    Designed to be called from FastAPI endpoints or other Python code.
    """

    A4_FREQ = 440.0
    SAMPLE_RATE = 44100
    NOTE_ORDER = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    ALT_NAMES = {"DB": "C#", "EB": "D#", "GB": "F#", "AB": "G#", "BB": "A#"}

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        default_volume: float = 0.8,
    ) -> None:
        self.sample_rate = int(sample_rate)
        self.default_volume = float(max(0.0, min(1.0, default_volume)))

    # ------- Public API -------

    def synthesize_tone(
        self,
        freq: float,
        duration: float = 1.0,
        *,
        volume: Optional[float] = None,
        waveform: str = "sine",
        attack: float = 0.01,
        release: float = 0.05,
    ) -> bytes:
        """Return WAV bytes for a tone at `freq` Hz.

        Args:
            freq: frequency in Hertz
            duration: seconds (> 0)
            volume: 0..1
            waveform: 'sine' | 'square' | 'triangle' | 'saw'
            attack: seconds (fade-in)
            release: seconds (fade-out)
        """
        if not (freq > 0):
            raise ValueError("freq must be > 0")
        if not (duration > 0):
            raise ValueError("duration must be > 0")

        volume = self._clamp(volume if volume is not None else self.default_volume, 0.0, 1.0)
        num_samples = int(self.sample_rate * duration)
        attack_samples = int(self.sample_rate * max(0.0, attack))
        release_samples = int(self.sample_rate * max(0.0, release))
        sustain_samples = max(0, num_samples - attack_samples - release_samples)

        # Generate raw floating samples in range [-1, 1]
        twopi_f_div_sr = 2.0 * math.pi * freq / self.sample_rate
        samples: List[float] = []

        if waveform == "sine":
            for n in range(num_samples):
                samples.append(math.sin(twopi_f_div_sr * n))
        elif waveform == "square":
            for n in range(num_samples):
                samples.append(1.0 if math.sin(twopi_f_div_sr * n) >= 0.0 else -1.0)
        elif waveform == "triangle":
            # Triangle via arc-sin(sin) approximation
            for n in range(num_samples):
                samples.append(2.0 / math.pi * math.asin(math.sin(twopi_f_div_sr * n)))
        elif waveform == "saw":
            for n in range(num_samples):
                t = (n / self.sample_rate) * freq
                samples.append(2.0 * (t - math.floor(0.5 + t)))
        else:
            raise ValueError("Unsupported waveform. Use 'sine' | 'square' | 'triangle' | 'saw'.")

        # Apply simple ADSR (attack-sustain-release)
        if attack_samples:
            for i in range(attack_samples):
                samples[i] *= (i + 1) / attack_samples
        if release_samples:
            for i in range(release_samples):
                idx = num_samples - release_samples + i
                if 0 <= idx < num_samples:
                    samples[idx] *= (1.0 - (i + 1) / release_samples)

        # No fancy sustain shaping; keep middle flat
        # Scale by volume and convert to 16-bit PCM
        pcm_bytes = self._float_to_pcm16(samples, volume)

        # Wrap as WAV
        wav_data = self._pcm_to_wav(pcm_bytes, self.sample_rate, num_channels=1, sampwidth=2)
        return wav_data

    def synthesize_note(
        self,
        note: str,
        octave: int = 4,
        duration: float = 1.0,
        *,
        volume: Optional[float] = None,
        waveform: str = "sine",
        attack: float = 0.01,
        release: float = 0.05,
    ) -> bytes:
        """Return WAV bytes for a musical note like C#, A, Bb."""
        freq = self.note_to_freq(note, octave)
        return self.synthesize_tone(
            freq,
            duration,
            volume=volume,
            waveform=waveform,
            attack=attack,
            release=release,
        )

    # ------- Helpers -------

    def note_to_freq(self, note: str, octave: int) -> float:
        if not isinstance(note, str):
            raise ValueError("note must be a string like 'A', 'C#', 'Bb'")
        name = note.strip().upper()
        name = name.replace("H", "B")  # support European H=B

        # Normalize flats to sharps
        name = self.ALT_NAMES.get(name, name)

        if name not in self.NOTE_ORDER:
            raise ValueError(f"Invalid note name '{note}'. Use one of {self.NOTE_ORDER} or flats Bb, Eb, Ab...")

        # MIDI number approach: A4 (MIDI 69) = 440 Hz
        semitone_index = self.NOTE_ORDER.index(name)
        midi_num = (octave + 1) * 12 + semitone_index  # MIDI standard: C-1 = 0
        n = midi_num - 69  # distance from A4
        freq = self.A4_FREQ * (2.0 ** (n / 12.0))
        return float(freq)

    @staticmethod
    def _clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, float(x)))

    @staticmethod
    def _float_to_pcm16(samples: Iterable[float], volume: float) -> bytes:
        # clamp and scale
        out = io.BytesIO()
        for s in samples:
            s = max(-1.0, min(1.0, float(s))) * volume
            out.write(struct.pack('<h', int(s * 32767.0)))
        return out.getvalue()

    @staticmethod
    def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int, num_channels: int, sampwidth: int) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_bytes)
        return buf.getvalue()

# ---------------------------
# FastAPI Router (optional)
# ---------------------------

BASE_AUDIO_DIR = Path("static") / "audio"
BASE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def _safe_join(base: Path, *paths: str) -> Path:
    """Join and ensure the result stays within `base`."""
    candidate = (base / Path(*paths)).resolve()
    base_res = base.resolve()
    try:
        candidate.relative_to(base_res)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path.")
    return candidate

def _detect_mime(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".wav":
        return "audio/wav"
    if ext == ".mp3":
        return "audio/mpeg"
    if ext == ".ogg":
        return "audio/ogg"
    if ext == ".m4a":
        return "audio/mp4"
    return "application/octet-stream"

def _file_chunker(path: Path, start: int, end: int, chunk_size: int = 64 * 1024) -> Generator[bytes, None, None]:
    with open(path, "rb") as f:
        f.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            read_size = min(chunk_size, remaining)
            data = f.read(read_size)
            if not data:
                break
            yield data
            remaining -= len(data)

def _serve_range_file(path: Path, range_header: Optional[str]) -> StreamingResponse:
    file_size = path.stat().st_size
    start = 0
    end = file_size - 1

    if range_header and range_header.startswith("bytes="):
        try:
            range_spec = range_header.split("=")[1].strip()
            # Support "start-end" or "start-"
            parts = range_spec.split("-")
            if parts[0]:
                start = int(parts[0])
            if len(parts) > 1 and parts[1]:
                end = int(parts[1])
            if start > end or end >= file_size:
                raise ValueError
        except Exception:
            raise HTTPException(status_code=416, detail="Invalid Range header")

        status_code = 206
    else:
        status_code = 200

    chunk_iter = _file_chunker(path, start, end)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Content-Length": str(end - start + 1),
        "Cache-Control": "public, max-age=3600",
    }
    return StreamingResponse(chunk_iter, media_type=_detect_mime(path), status_code=status_code, headers=headers)

# Expose router only if FastAPI is installed
if APIRouter is not None:
    router = APIRouter(prefix="/audio", tags=["audio"])

    @router.get("/list")
    def list_audio_files() -> List[str]:
        """List files under ./static/audio (relative names)."""
        files = []
        for p in BASE_AUDIO_DIR.glob("**/*"):
            if p.is_file():
                files.append(str(p.relative_to(BASE_AUDIO_DIR)))
        return files

    @router.get("/stream/{relpath:path}")
    def stream_audio(relpath: str, request: Request):
        """Stream a static audio file with HTTP Range support (HTML5 <audio> friendly)."""
        path = _safe_join(BASE_AUDIO_DIR, relpath)
        if not path.exists() or not path.is_file():
            raise HTTPException(status_code=404, detail="File not found")

        range_header = request.headers.get("Range")
        return _serve_range_file(path, range_header)

    @router.get("/note")
    def synth_note(
        note: str = Query(..., description="Note name, e.g., A, C#, Bb"),
        octave: int = Query(4, ge=0, le=8),
        duration: float = Query(1.0, gt=0, le=10.0),
        waveform: str = Query("sine", pattern="^(sine|square|triangle|saw)$"),
        volume: float = Query(0.8, ge=0.0, le=1.0),
    ) -> Response:
        """Synthesize a note on the fly and return WAV bytes."""
        ap = AudioPlayer()
        try:
            data = ap.synthesize_note(note=note, octave=octave, duration=duration, waveform=waveform, volume=volume)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return Response(content=data, media_type="audio/wav")

    @router.get("/tone")
    def synth_tone(
        freq: float = Query(..., gt=0, description="Frequency in Hz"),
        duration: float = Query(1.0, gt=0, le=10.0),
        waveform: str = Query("sine", pattern="^(sine|square|triangle|saw)$"),
        volume: float = Query(0.8, ge=0.0, le=1.0),
    ) -> Response:
        ap = AudioPlayer()
        data = ap.synthesize_tone(freq=freq, duration=duration, waveform=waveform, volume=volume)
        return Response(content=data, media_type="audio/wav")
else:  # FastAPI not available - expose a placeholder so import doesn't fail
    router = None  # type: ignore
