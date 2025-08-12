import librosa
import numpy as np
import music21 as m21
from typing import List, Tuple, Dict

class AudioAnalyzer:
    """Classe para análise de áudio musical usando librosa e music21."""
    
    def __init__(self):
        self.sample_rate = 22050  # Taxa de amostragem padrão do librosa
        
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Carrega um arquivo de áudio."""
        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            return y, sr
        except Exception as e:
            raise Exception(f"Erro ao carregar áudio: {str(e)}")
    
    def detect_key(self, y: np.ndarray, sr: int) -> str:
        """Detecta a tonalidade da música usando análise de croma."""
        try:
            # Extrai características de croma
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Calcula a média das características de croma
            chroma_mean = np.mean(chroma, axis=1)
            
            # Nomes das notas
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            
            # Encontra a nota com maior energia
            dominant_note_idx = np.argmax(chroma_mean)
            dominant_note = note_names[dominant_note_idx]
            
            # Análise simples para determinar se é maior ou menor
            # Baseado na presença de terças maiores vs menores
            major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])  # Perfil de escala maior
            minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])  # Perfil de escala menor
            
            # Rotaciona os perfis para a nota dominante
            major_rotated = np.roll(major_profile, dominant_note_idx)
            minor_rotated = np.roll(minor_profile, dominant_note_idx)
            
            # Calcula correlação
            major_corr = np.corrcoef(chroma_mean, major_rotated)[0, 1]
            minor_corr = np.corrcoef(chroma_mean, minor_rotated)[0, 1]
            
            # Determina se é maior ou menor
            if major_corr > minor_corr:
                return f"{dominant_note} maior"
            else:
                return f"{dominant_note} menor"
                
        except Exception as e:
            return f"Erro na detecção de tonalidade: {str(e)}"
    
    def detect_tempo(self, y: np.ndarray, sr: int) -> float:
        """Detecta o tempo (BPM) da música."""
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            return float(tempo)
        except Exception as e:
            return 0.0
    
    def extract_chroma_features(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extrai características de croma para análise harmônica."""
        try:
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            return chroma
        except Exception as e:
            return np.array([])
    
    def simple_chord_detection(self, y: np.ndarray, sr: int, hop_length: int = 512) -> List[str]:
        """Detecção simples de acordes baseada em templates."""
        try:
            # Extrai características de croma
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
            
            # Templates básicos para acordes maiores e menores
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            
            # Templates para acordes maiores (1, 3, 5)
            major_templates = {}
            for i, note in enumerate(note_names):
                template = np.zeros(12)
                template[i] = 1.0  # Fundamental
                template[(i + 4) % 12] = 0.8  # Terça maior
                template[(i + 7) % 12] = 0.6  # Quinta
                major_templates[f"{note}"] = template
            
            # Templates para acordes menores (1, b3, 5)
            minor_templates = {}
            for i, note in enumerate(note_names):
                template = np.zeros(12)
                template[i] = 1.0  # Fundamental
                template[(i + 3) % 12] = 0.8  # Terça menor
                template[(i + 7) % 12] = 0.6  # Quinta
                minor_templates[f"{note}m"] = template
            
            # Combina todos os templates
            all_templates = {**major_templates, **minor_templates}
            
            # Detecta acordes frame por frame
            detected_chords = []
            for frame in range(chroma.shape[1]):
                frame_chroma = chroma[:, frame]
                
                best_match = ""
                best_score = -1
                
                for chord_name, template in all_templates.items():
                    # Calcula correlação
                    score = np.corrcoef(frame_chroma, template)[0, 1]
                    if not np.isnan(score) and score > best_score:
                        best_score = score
                        best_match = chord_name
                
                detected_chords.append(best_match if best_score > 0.5 else "N")
            
            return detected_chords
            
        except Exception as e:
            return [f"Erro: {str(e)}"]
    
    def analyze_audio_file(self, file_path: str) -> Dict:
        """Análise completa de um arquivo de áudio."""
        try:
            # Carrega o áudio
            y, sr = self.load_audio(file_path)
            
            # Realiza análises
            key = self.detect_key(y, sr)
            tempo = self.detect_tempo(y, sr)
            chords = self.simple_chord_detection(y, sr)
            
            # Simplifica a lista de acordes (pega acordes únicos em sequência)
            simplified_chords = []
            prev_chord = ""
            for chord in chords:
                if chord != prev_chord and chord != "N":
                    simplified_chords.append(chord)
                    prev_chord = chord
            
            return {
                "tonalidade": key,
                "tempo": tempo,
                "acordes_detectados": simplified_chords[:10],  # Primeiros 10 acordes
                "duracao": len(y) / sr
            }
            
        except Exception as e:
            return {"erro": str(e)}

# Função auxiliar para gerar cifras básicas
def generate_basic_chord_progression(key: str) -> List[str]:
    """Gera uma progressão de acordes básica para uma tonalidade."""
    try:
        # Remove "maior" ou "menor" da string da tonalidade
        if "maior" in key:
            tonic = key.replace(" maior", "")
            mode = "major"
        elif "menor" in key:
            tonic = key.replace(" menor", "")
            mode = "minor"
        else:
            return ["Tonalidade não reconhecida"]
        
        # Cria objeto de tonalidade no music21
        key_obj = m21.key.Key(tonic, mode)
        
        # Gera campo harmônico
        chords = []
        for degree in range(1, 8):
            chord = key_obj.getChord(degree)
            chords.append(chord.commonName)
        
        return chords
        
    except Exception as e:
        return [f"Erro: {str(e)}"]
