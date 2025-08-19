import librosa
import numpy as np
from typing import Dict, List, Tuple
import music21 as m21
from scipy.signal import find_peaks
from sklearn.cluster import KMeans

class AudioAnalyzer:
    """Classe para análise avançada de áudio musical."""
    
    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Perfis de tonalidade Krumhansl-Schmuckler otimizados
        self.major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        self.minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Templates de acordes expandidos com pesos otimizados
        self.chord_templates = {
            'major': [1.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.9, 0.0, 0.0, 0.0, 0.0],
            'minor': [1.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.9, 0.0, 0.0, 0.0, 0.0],
            'dim': [1.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0],
            'aug': [1.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.7, 0.0, 0.0, 0.0],
            'sus2': [1.0, 0.0, 0.7, 0.0, 0.0, 0.0, 0.0, 0.9, 0.0, 0.0, 0.0, 0.0],
            'sus4': [1.0, 0.0, 0.0, 0.0, 0.0, 0.7, 0.0, 0.9, 0.0, 0.0, 0.0, 0.0],
            'maj7': [1.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.9, 0.0, 0.0, 0.0, 0.7],
            'min7': [1.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.9, 0.0, 0.0, 0.6, 0.0],
            'dom7': [1.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.9, 0.0, 0.0, 0.7, 0.0],
            'dim7': [1.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.7, 0.0, 0.0, 0.6, 0.0, 0.0],
            'maj9': [1.0, 0.0, 0.6, 0.0, 0.8, 0.0, 0.0, 0.9, 0.0, 0.0, 0.0, 0.7],
            'min9': [1.0, 0.0, 0.6, 0.8, 0.0, 0.0, 0.0, 0.9, 0.0, 0.0, 0.6, 0.0],
            'add9': [1.0, 0.0, 0.5, 0.0, 0.8, 0.0, 0.0, 0.9, 0.0, 0.0, 0.0, 0.0],
            'min6': [1.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.9, 0.0, 0.6, 0.0, 0.0],
            'maj6': [1.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.9, 0.0, 0.6, 0.0, 0.0]
        }
        
        # Configurações de análise otimizadas
        self.segment_length = 3.0  # segundos por segmento
        self.overlap_ratio = 0.5   # 50% de sobreposição entre segmentos
        self.min_chord_confidence = 0.65  # Confiança mínima para detecção de acordes
        self.key_change_threshold = 0.15   # Limiar para detectar mudanças de tonalidade
    
    def analyze_audio_file(self, file_path: str) -> Dict:
        """Analisa um arquivo de áudio com algoritmos otimizados."""
        try:
            # Carrega o áudio com parâmetros otimizados
            y, sr = librosa.load(file_path, sr=22050)
            
            # Análise básica
            duration = len(y) / sr
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
            
            # Análise de croma com parâmetros otimizados
            hop_length = 512
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length, 
                                               fmin=librosa.note_to_hz('C2'),
                                               n_chroma=12, norm=2)
            
            # Suavização do croma para reduzir ruído
            chroma = self.smooth_chroma(chroma)
            
            # Detecção de tonalidade global melhorada
            global_key, key_confidence = self.detect_key_krumhansl_schmuckler_enhanced(chroma)
            
            # Análise segmentada otimizada
            segmented_analysis, key_changes = self.analyze_segments_optimized(chroma, sr, hop_length, duration)
            
            # Detecção de acordes globais melhorada
            global_chords = self.detect_chords_global_enhanced(chroma)
            
            # Análise de estrutura musical
            structure_analysis = self.analyze_musical_structure(chroma, beats)
            
            # Análise de progressões harmônicas
            harmonic_progressions = self.analyze_harmonic_progressions(segmented_analysis)
            
            return {
                'tonalidade_global': global_key,
                'confianca_tonalidade': key_confidence,
                'tempo': float(tempo),
                'duracao': duration,
                'acordes_globais_detectados': global_chords,
                'analise_segmentada': segmented_analysis,
                'mudancas_tonalidade': key_changes,
                'estrutura_musical': structure_analysis,
                'progressoes_harmonicas': harmonic_progressions
            }
            
        except Exception as e:
            return {'erro': str(e)}
    
    def smooth_chroma(self, chroma: np.ndarray, window_size: int = 5) -> np.ndarray:
        """Aplica suavização temporal ao croma para reduzir ruído."""
        from scipy.ndimage import uniform_filter1d
        return uniform_filter1d(chroma, size=window_size, axis=1)
    
    def detect_key_krumhansl_schmuckler_enhanced(self, chroma: np.ndarray) -> Tuple[str, float]:
        """Detecta tonalidade com algoritmo Krumhansl-Schmuckler melhorado."""
        # Calcula o perfil de croma médio com pesos temporais
        weights = np.linspace(0.8, 1.2, chroma.shape[1])  # Dá mais peso ao final
        chroma_weighted = chroma * weights
        chroma_mean = np.mean(chroma_weighted, axis=1)
        
        # Normaliza o perfil
        if np.sum(chroma_mean) > 0:
            chroma_mean = chroma_mean / np.sum(chroma_mean)
        
        correlations = []
        
        # Testa todas as 24 tonalidades
        for i in range(12):
            # Tonalidade maior
            major_template = np.roll(self.major_profile, i)
            major_template = major_template / np.sum(major_template)
            major_corr = np.corrcoef(chroma_mean, major_template)[0, 1]
            if not np.isnan(major_corr):
                correlations.append((major_corr, f"{self.note_names[i]} maior"))
            
            # Tonalidade menor
            minor_template = np.roll(self.minor_profile, i)
            minor_template = minor_template / np.sum(minor_template)
            minor_corr = np.corrcoef(chroma_mean, minor_template)[0, 1]
            if not np.isnan(minor_corr):
                correlations.append((minor_corr, f"{self.note_names[i]} menor"))
        
        # Retorna a tonalidade com maior correlação
        correlations.sort(reverse=True)
        best_correlation, best_key = correlations[0]
        
        return best_key, float(best_correlation)
    
    def analyze_segments_optimized(self, chroma: np.ndarray, sr: int, hop_length: int, duration: float) -> Tuple[List[Dict], List[Dict]]:
        """Análise segmentada otimizada com sobreposição."""
        frames_per_segment = int(self.segment_length * sr / hop_length)
        hop_frames = int(frames_per_segment * (1 - self.overlap_ratio))
        
        segmented_analysis = []
        key_changes = []
        previous_key = None
        previous_confidence = 0
        
        for i in range(0, chroma.shape[1] - frames_per_segment + 1, hop_frames):
            start_time = i * hop_length / sr
            end_time = min((i + frames_per_segment) * hop_length / sr, duration)
            
            # Extrai segmento de croma
            segment_chroma = chroma[:, i:i+frames_per_segment]
            
            if segment_chroma.shape[1] > 0:
                # Detecção de tonalidade do segmento
                segment_key, key_confidence = self.detect_key_krumhansl_schmuckler_enhanced(segment_chroma)
                
                # Detecção de acordes do segmento
                segment_chords = self.detect_chords_in_segment_enhanced(segment_chroma)
                
                # Análise de estabilidade harmônica
                harmonic_stability = self.calculate_harmonic_stability(segment_chroma)
                
                segmented_analysis.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'tonalidade_segmento': segment_key,
                    'confianca_tonalidade': key_confidence,
                    'acordes_segmento': segment_chords,
                    'estabilidade_harmonica': harmonic_stability
                })
                
                # Detecta mudanças de tonalidade significativas
                if (previous_key and previous_key != segment_key and 
                    abs(key_confidence - previous_confidence) > self.key_change_threshold):
                    key_changes.append({
                        'time': start_time,
                        'from_key': previous_key,
                        'to_key': segment_key,
                        'confidence_change': abs(key_confidence - previous_confidence)
                    })
                
                previous_key = segment_key
                previous_confidence = key_confidence
        
        return segmented_analysis, key_changes
    
    def detect_chords_global_enhanced(self, chroma: np.ndarray) -> List[str]:
        """Detecta acordes predominantes com algoritmo melhorado."""
        detected_chords = {}
        
        # Analisa janelas menores para maior precisão
        window_size = 22  # ~1 segundo
        
        for i in range(0, chroma.shape[1], window_size // 2):  # 50% overlap
            window_chroma = chroma[:, i:i+window_size]
            if window_chroma.shape[1] > 0:
                chord, confidence = self.detect_chord_in_window_enhanced(np.mean(window_chroma, axis=1))
                if chord and confidence > self.min_chord_confidence:
                    if chord in detected_chords:
                        detected_chords[chord] += confidence
                    else:
                        detected_chords[chord] = confidence
        
        # Ordena por confiança e retorna os mais prováveis
        sorted_chords = sorted(detected_chords.items(), key=lambda x: x[1], reverse=True)
        return [chord for chord, _ in sorted_chords[:8]]
    
    def detect_chords_in_segment_enhanced(self, segment_chroma: np.ndarray) -> List[str]:
        """Detecta acordes em um segmento com maior precisão."""
        detected_chords = {}
        
        # Analisa sub-janelas dentro do segmento
        sub_window_size = 11  # ~0.5 segundos
        
        for i in range(0, segment_chroma.shape[1], sub_window_size // 2):
            window_chroma = segment_chroma[:, i:i+sub_window_size]
            if window_chroma.shape[1] > 0:
                chord, confidence = self.detect_chord_in_window_enhanced(np.mean(window_chroma, axis=1))
                if chord and confidence > self.min_chord_confidence:
                    if chord in detected_chords:
                        detected_chords[chord] += confidence
                    else:
                        detected_chords[chord] = confidence
        
        # Retorna acordes ordenados por confiança
        sorted_chords = sorted(detected_chords.items(), key=lambda x: x[1], reverse=True)
        return [chord for chord, _ in sorted_chords[:4]]
    
    def detect_chord_in_window_enhanced(self, chroma_vector: np.ndarray) -> Tuple[str, float]:
        """Detecta acorde com maior precisão e retorna confiança."""
        # Normaliza o vetor de croma
        if np.sum(chroma_vector) > 0:
            chroma_vector = chroma_vector / np.sum(chroma_vector)
        else:
            return None, 0.0
        
        best_match = None
        best_score = -1
        
        # Testa todos os acordes em todas as transposições
        for root in range(12):
            for chord_type, template in self.chord_templates.items():
                # Transpõe o template para a raiz atual
                transposed_template = np.roll(template, root)
                transposed_template = np.array(transposed_template, dtype=float)
                
                # Normaliza o template
                if np.sum(transposed_template) > 0:
                    transposed_template = transposed_template / np.sum(transposed_template)
                
                # Calcula correlação ponderada
                correlation = self.calculate_weighted_correlation(chroma_vector, transposed_template)
                
                if not np.isnan(correlation) and correlation > best_score:
                    best_score = correlation
                    chord_name = f"{self.note_names[root]}{chord_type if chord_type != 'major' else ''}"
                    best_match = chord_name
        
        return best_match, float(best_score) if best_match else (None, 0.0)
    
    def calculate_weighted_correlation(self, chroma1: np.ndarray, chroma2: np.ndarray) -> float:
        """Calcula correlação ponderada dando mais peso às notas fundamentais."""
        # Pesos para cada nota (dá mais importância às fundamentais)
        weights = np.array([1.0, 0.7, 0.8, 0.9, 1.0, 0.8, 0.7, 1.0, 0.8, 0.8, 0.7, 0.8])
        
        weighted_chroma1 = chroma1 * weights
        weighted_chroma2 = chroma2 * weights
        
        correlation = np.corrcoef(weighted_chroma1, weighted_chroma2)[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    
    def calculate_harmonic_stability(self, chroma: np.ndarray) -> float:
        """Calcula a estabilidade harmônica de um segmento."""
        # Calcula a variância temporal do croma
        chroma_var = np.var(chroma, axis=1)
        stability = 1.0 - np.mean(chroma_var)
        return max(0.0, min(1.0, stability))
    
    def analyze_musical_structure(self, chroma: np.ndarray, beats: np.ndarray) -> Dict:
        """Analisa a estrutura musical (verso, refrão, etc.)."""
        try:
            # Usa clustering para identificar seções similares
            segment_size = 44  # ~2 segundos
            segments = []
            
            for i in range(0, chroma.shape[1] - segment_size, segment_size // 2):
                segment = chroma[:, i:i+segment_size]
                segments.append(np.mean(segment, axis=1))
            
            if len(segments) > 3:
                # Aplica K-means para identificar seções
                n_clusters = min(4, len(segments) // 2)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = kmeans.fit_predict(segments)
                
                # Mapeia clusters para seções musicais
                section_names = ['Intro', 'Verso', 'Refrão', 'Ponte']
                sections = []
                
                for i, label in enumerate(labels):
                    start_time = i * segment_size * 512 / 22050 / 2  # Conversão para segundos
                    sections.append({
                        'section': section_names[label % len(section_names)],
                        'start_time': start_time,
                        'cluster_id': int(label)
                    })
                
                return {
                    'sections': sections,
                    'n_sections': n_clusters,
                    'structure_confidence': float(np.mean(kmeans.cluster_centers_))
                }
            else:
                return {'sections': [], 'n_sections': 0, 'structure_confidence': 0.0}
                
        except Exception:
            return {'sections': [], 'n_sections': 0, 'structure_confidence': 0.0}
    
    def analyze_harmonic_progressions(self, segmented_analysis: List[Dict]) -> List[Dict]:
        """Analisa progressões harmônicas entre segmentos."""
        progressions = []
        
        for i in range(len(segmented_analysis) - 1):
            current_segment = segmented_analysis[i]
            next_segment = segmented_analysis[i + 1]
            
            current_chords = current_segment.get('acordes_segmento', [])
            next_chords = next_segment.get('acordes_segmento', [])
            
            if current_chords and next_chords:
                # Analisa a transição entre acordes
                progression_type = self.classify_progression(current_chords, next_chords)
                
                progressions.append({
                    'start_time': current_segment['start_time'],
                    'end_time': next_segment['end_time'],
                    'from_chords': current_chords,
                    'to_chords': next_chords,
                    'progression_type': progression_type
                })
        
        return progressions
    
    def classify_progression(self, chords1: List[str], chords2: List[str]) -> str:
        """Classifica o tipo de progressão harmônica."""
        # Análise simplificada de progressões comuns
        common_progressions = {
            ('C', 'F'): 'I-IV',
            ('C', 'G'): 'I-V',
            ('Am', 'F'): 'vi-IV',
            ('F', 'G'): 'IV-V',
            ('G', 'C'): 'V-I',
            ('Am', 'C'): 'vi-I'
        }
        
        # Verifica se há progressões conhecidas
        for chord1 in chords1:
            for chord2 in chords2:
                # Remove sufixos para comparação básica
                root1 = chord1.split('m')[0].split('7')[0].split('dim')[0]
                root2 = chord2.split('m')[0].split('7')[0].split('dim')[0]
                
                if (root1, root2) in common_progressions:
                    return common_progressions[(root1, root2)]
        
        return 'Progressão personalizada'

def generate_basic_chord_progression(key: str) -> List[str]:
    """Gera uma progressão de acordes básica baseada na tonalidade."""
    try:
        # Extrai a tônica e o modo da tonalidade
        parts = key.split()
        if len(parts) >= 2:
            tonic = parts[0]
            mode = parts[1].lower()
        else:
            return []
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        if tonic not in note_names:
            return []
        
        root_idx = note_names.index(tonic)
        
        if mode == "maior":
            # Campo harmônico maior: I - ii - iii - IV - V - vi - vii°
            intervals = [0, 2, 4, 5, 7, 9, 11]
            qualities = ["", "m", "m", "", "", "m", "dim"]
            # Progressões mais variadas
            progression_options = [
                [0, 3, 4, 0],  # I - IV - V - I
                [0, 5, 3, 4],  # I - vi - IV - V
                [5, 3, 0, 4],  # vi - IV - I - V
                [0, 1, 3, 4]   # I - ii - IV - V
            ]
        else:  # menor
            # Campo harmônico menor: i - ii° - III - iv - v - VI - VII
            intervals = [0, 2, 3, 5, 7, 8, 10]
            qualities = ["m", "dim", "", "m", "m", "", ""]
            progression_options = [
                [0, 3, 4, 0],  # i - iv - v - i
                [0, 5, 6, 0],  # i - VI - VII - i
                [0, 2, 5, 6],  # i - III - VI - VII
                [0, 3, 5, 4]   # i - iv - VI - v
            ]
        
        # Escolhe uma progressão aleatoriamente
        import random
        progression_degrees = random.choice(progression_options)
        
        progression = []
        for degree in progression_degrees:
            chord_root = note_names[(root_idx + intervals[degree]) % 12]
            chord_quality = qualities[degree]
            progression.append(f"{chord_root}{chord_quality}")
        
        return progression
        
    except Exception:
        return []

