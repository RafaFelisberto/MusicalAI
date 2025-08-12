import music21 as m21
from typing import List, Dict, Tuple, Optional, Any
import random
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ChordQuality(Enum):
    """Enumeração para qualidades de acordes."""
    MAJOR = "major"
    MINOR = "minor"
    DOMINANT_7 = "7"
    MAJOR_7 = "maj7"
    MINOR_7 = "m7"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    HALF_DIMINISHED = "m7b5"

class ScaleType(Enum):
    """Enumeração para tipos de escalas."""
    MAJOR = "major"
    MINOR = "minor"
    HARMONIC_MINOR = "harmonic_minor"
    MELODIC_MINOR = "melodic_minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    AEOLIAN = "aeolian"
    LOCRIAN = "locrian"

@dataclass
class ChordInfo:
    """Classe para informações de acordes."""
    name: str
    root: str
    quality: str
    notes: List[str]
    intervals: List[str]
    function: str
    roman_numeral: str

@dataclass
class ScaleInfo:
    """Classe para informações de escalas."""
    name: str
    tonic: str
    notes: List[str]
    intervals: List[int]
    pattern: str
    description: str

class MusicTheoryTeacher:
    """Sistema aprimorado para ensino de teoria musical."""
    
    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.note_names_flat = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        
        self.setup_intervals()
        self.setup_modes()
        self.setup_chord_functions()
        self.setup_progressions()
        
        logger.info("MusicTheoryTeacher inicializado")
    
    def setup_intervals(self):
        """Configura informações sobre intervalos."""
        self.intervals = {
            0: {"name": "Uníssono", "quality": "Perfeito", "semitones": 0},
            1: {"name": "2ª menor", "quality": "Menor", "semitones": 1},
            2: {"name": "2ª maior", "quality": "Maior", "semitones": 2},
            3: {"name": "3ª menor", "quality": "Menor", "semitones": 3},
            4: {"name": "3ª maior", "quality": "Maior", "semitones": 4},
            5: {"name": "4ª justa", "quality": "Perfeito", "semitones": 5},
            6: {"name": "Trítono", "quality": "Aumentado/Diminuto", "semitones": 6},
            7: {"name": "5ª justa", "quality": "Perfeito", "semitones": 7},
            8: {"name": "6ª menor", "quality": "Menor", "semitones": 8},
            9: {"name": "6ª maior", "quality": "Maior", "semitones": 9},
            10: {"name": "7ª menor", "quality": "Menor", "semitones": 10},
            11: {"name": "7ª maior", "quality": "Maior", "semitones": 11},
            12: {"name": "Oitava", "quality": "Perfeito", "semitones": 12}
        }
        
        # Exemplos musicais para intervalos
        self.interval_examples = {
            1: "Início de 'Für Elise' (Beethoven)",
            2: "Início de 'Happy Birthday'",
            3: "Início de 'Greensleeves'",
            4: "Início de 'When the Saints Go Marching In'",
            5: "Início de 'Here Comes the Bride'",
            6: "Abertura de 'The Simpsons'",
            7: "Início de 'Twinkle, Twinkle, Little Star'",
            8: "Início de 'My Way' (Frank Sinatra)",
            9: "Início de 'Take On Me' (A-ha)",
            10: "Acorde C7 (C para Bb)",
            11: "Início de 'Take Five' (Dave Brubeck)",
            12: "Início de 'Somewhere Over the Rainbow'"
        }
    
    def setup_modes(self):
        """Configura informações sobre modos."""
        self.modes = {
            "jônio": {
                "intervals": [0, 2, 4, 5, 7, 9, 11],
                "pattern": "T-T-S-T-T-T-S",
                "description": "Modo maior tradicional, som alegre e brilhante",
                "characteristic": "4ª e 7ª justas",
                "genres": ["Pop", "Rock", "Música clássica", "Country"],
                "mood": "Alegre, estável, resolutivo"
            },
            "dórico": {
                "intervals": [0, 2, 3, 5, 7, 9, 10],
                "pattern": "T-S-T-T-T-S-T",
                "description": "Som menor com 6ª maior, menos melancólico que o menor natural",
                "characteristic": "6ª maior (diferente do menor natural)",
                "genres": ["Jazz", "Música celta", "Rock progressivo", "Fusion"],
                "mood": "Melancólico mas esperançoso"
            },
            "frígio": {
                "intervals": [0, 1, 3, 5, 7, 8, 10],
                "pattern": "S-T-T-T-S-T-T",
                "description": "Som menor com 2ª menor, muito usado no flamenco",
                "characteristic": "2ª menor (muito característico)",
                "genres": ["Flamenco", "Metal", "Música espanhola", "Música árabe"],
                "mood": "Exótico, dramático, misterioso"
            },
            "lídio": {
                "intervals": [0, 2, 4, 6, 7, 9, 11],
                "pattern": "T-T-T-S-T-T-S",
                "description": "Som maior com 4ª aumentada, cria sonoridade etérea",
                "characteristic": "4ª aumentada (som 'mágico')",
                "genres": ["Jazz fusion", "Trilhas sonoras", "Música new age", "Progressive rock"],
                "mood": "Etéreo, flutuante, onírico"
            },
            "mixolídio": {
                "intervals": [0, 2, 4, 5, 7, 9, 10],
                "pattern": "T-T-S-T-T-S-T",
                "description": "Som maior com 7ª menor, muito usado no blues e rock",
                "characteristic": "7ª menor (diferente do maior)",
                "genres": ["Blues", "Rock", "Folk", "Música irlandesa"],
                "mood": "Relaxado, bluesy, terreno"
            },
            "eólio": {
                "intervals": [0, 2, 3, 5, 7, 8, 10],
                "pattern": "T-S-T-T-S-T-T",
                "description": "Modo menor natural, som melancólico e introspectivo",
                "characteristic": "3ª, 6ª e 7ª menores",
                "genres": ["Rock", "Pop", "Música clássica", "Folk"],
                "mood": "Melancólico, introspectivo, nostálgico"
            },
            "lócrio": {
                "intervals": [0, 1, 3, 5, 6, 8, 10],
                "pattern": "S-T-T-S-T-T-T",
                "description": "Modo mais instável, com 5ª diminuta",
                "characteristic": "2ª menor e 5ª diminuta",
                "genres": ["Jazz experimental", "Metal extremo", "Música contemporânea"],
                "mood": "Instável, tenso, dissonante"
            }
        }
    
    def setup_chord_functions(self):
        """Configura funções harmônicas."""
        self.chord_functions = {
            "major": {
                1: {"function": "Tônica", "description": "Centro tonal, repouso", "tension": "Relaxamento"},
                2: {"function": "Subdominante", "description": "Preparação, afastamento suave", "tension": "Baixa"},
                3: {"function": "Mediante", "description": "Tônica relativa, cor harmônica", "tension": "Baixa"},
                4: {"function": "Subdominante", "description": "Afastamento do centro tonal", "tension": "Média"},
                5: {"function": "Dominante", "description": "Máxima tensão, resolve na tônica", "tension": "Alta"},
                6: {"function": "Superdominante", "description": "Tônica relativa, início de progressões", "tension": "Baixa"},
                7: {"function": "Sensível", "description": "Tensão que resolve na tônica", "tension": "Alta"}
            },
            "minor": {
                1: {"function": "Tônica", "description": "Centro tonal menor", "tension": "Relaxamento"},
                2: {"function": "Supertônica", "description": "Preparação diminuta", "tension": "Média"},
                3: {"function": "Mediante", "description": "Relativa maior", "tension": "Baixa"},
                4: {"function": "Subdominante", "description": "Afastamento menor", "tension": "Média"},
                5: {"function": "Dominante", "description": "Tensão menor", "tension": "Média-Alta"},
                6: {"function": "Superdominante", "description": "Subdominante relativa", "tension": "Baixa"},
                7: {"function": "Subtônica", "description": "Tensão natural menor", "tension": "Média"}
            }
        }
    
    def setup_progressions(self):
        """Configura progressões harmônicas comuns."""
        self.common_progressions = {
            "major": {
                "Pop clássico": ["I", "V", "vi", "IV"],
                "Anos 50": ["I", "vi", "IV", "V"],
                "Canon": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"],
                "Cadência autêntica": ["I", "IV", "V", "I"],
                "Cadência plagal": ["I", "IV", "I"],
                "Circle progression": ["vi", "ii", "V", "I"]
            },
            "minor": {
                "Menor clássico": ["i", "VII", "VI", "VII"],
                "Cadência menor": ["i", "iv", "V", "i"],
                "Progressão andaluza": ["i", "VII", "VI", "V"],
                "Menor melancólico": ["i", "v", "iv", "i"],
                "Modal interchange": ["i", "VI", "III", "VII"]
            }
        }
    
    def explain_scale(self, tonic: str, scale_type: str = "major") -> Dict[str, Any]:
        """Explica uma escala musical com informações detalhadas."""
        try:
            logger.info(f"Explicando escala: {tonic} {scale_type}")
            
            tonic = tonic.upper()
            if tonic not in self.note_names:
                return {"erro": f"Nota '{tonic}' não reconhecida"}
            
            tonic_index = self.note_names.index(tonic)
            
            # Determina os intervalos da escala
            if scale_type.lower() in ["major", "maior"]:
                intervals = [0, 2, 4, 5, 7, 9, 11]
                pattern = "T-T-S-T-T-T-S"
                description = "A escala maior tem um som alegre e brilhante, sendo a base da música tonal ocidental."
                scale_name = f"{tonic} maior"
            elif scale_type.lower() in ["minor", "menor", "natural_minor"]:
                intervals = [0, 2, 3, 5, 7, 8, 10]
                pattern = "T-S-T-T-S-T-T"
                description = "A escala menor natural tem um som melancólico e introspectivo."
                scale_name = f"{tonic} menor"
            elif scale_type.lower() == "harmonic_minor":
                intervals = [0, 2, 3, 5, 7, 8, 11]
                pattern = "T-S-T-T-S-T+S-S"
                description = "A escala menor harmônica tem uma 7ª maior, criando um som exótico."
                scale_name = f"{tonic} menor harmônica"
            elif scale_type.lower() == "melodic_minor":
                intervals = [0, 2, 3, 5, 7, 9, 11]
                pattern = "T-S-T-T-T-T-S"
                description = "A escala menor melódica ascendente tem 6ª e 7ª maiores."
                scale_name = f"{tonic} menor melódica"
            else:
                return {"erro": f"Tipo de escala '{scale_type}' não reconhecido"}
            
            # Calcula as notas da escala
            notes = [self.note_names[(tonic_index + interval) % 12] for interval in intervals]
            
            # Graus da escala
            degrees = ["I", "II", "III", "IV", "V", "VI", "VII"]
            
            # Informações adicionais
            chord_qualities = self.get_scale_chord_qualities(scale_type.lower())
            
            result = {
                "escala": scale_name,
                "notas": notes,
                "graus": degrees,
                "padrao": pattern,
                "descricao": description,
                "intervalos": intervals,
                "acordes_da_escala": [f"{note}{quality}" for note, quality in zip(notes, chord_qualities)]
            }
            
            # Adiciona modos relacionados se for escala maior
            if scale_type.lower() in ["major", "maior"]:
                result["modos_relacionados"] = self.get_related_modes(tonic)
            
            logger.info(f"Escala explicada com sucesso: {scale_name}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao explicar escala: {str(e)}")
            return {"erro": f"Erro interno: {str(e)}"}
    
    def explain_chord(self, root: str, chord_type: str = "major") -> Dict[str, Any]:
        """Explica a formação de um acorde com informações detalhadas."""
        try:
            logger.info(f"Explicando acorde: {root}{chord_type}")
            
            root = root.upper()
            if root not in self.note_names:
                return {"erro": f"Nota '{root}' não reconhecida"}
            
            root_index = self.note_names.index(root)
            
            # Determina intervalos e características do acorde
            chord_info = self.get_chord_intervals_and_info(chord_type.lower())
            if "erro" in chord_info:
                return chord_info
            
            # Calcula as notas do acorde
            chord_notes = [self.note_names[(root_index + interval) % 12] 
                          for interval in chord_info["intervals"]]
            
            # Nomes dos intervalos
            interval_names = [self.intervals[interval]["name"] for interval in chord_info["intervals"]]
            
            result = {
                "acorde": f"{root}{chord_info['symbol']}",
                "notas": chord_notes,
                "intervalos": interval_names,
                "descricao": chord_info["description"],
                "cifra": f"{root}{chord_info['symbol']}",
                "funcao": chord_info["function"],
                "tensao": chord_info["tension"],
                "uso_comum": chord_info["common_use"],
                "exemplo_progressao": self.suggest_chord_progression(root, chord_type),
                "inversoes": self.get_chord_inversions(chord_notes)
            }
            
            logger.info(f"Acorde explicado com sucesso: {root}{chord_type}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao explicar acorde: {str(e)}")
            return {"erro": f"Erro interno: {str(e)}"}
    
    def explain_harmonic_field(self, tonic: str, mode: str = "major") -> Dict[str, Any]:
        """Explica o campo harmônico com análise funcional completa."""
        try:
            logger.info(f"Explicando campo harmônico: {tonic} {mode}")
            
            tonic = tonic.upper()
            if tonic not in self.note_names:
                return {"erro": f"Nota '{tonic}' não reconhecida"}
            
            tonic_index = self.note_names.index(tonic)
            mode_lower = mode.lower()
            
            # Determina intervalos e qualidades dos acordes
            if mode_lower in ["major", "maior"]:
                intervals = [0, 2, 4, 5, 7, 9, 11]
                chord_qualities = ["", "m", "m", "", "", "m", "dim"]
                roman_numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
                mode_name = "maior"
            elif mode_lower in ["minor", "menor"]:
                intervals = [0, 2, 3, 5, 7, 8, 10]
                chord_qualities = ["m", "dim", "", "m", "m", "", ""]
                roman_numerals = ["i", "ii°", "III", "iv", "v", "VI", "VII"]
                mode_name = "menor"
            else:
                return {"erro": f"Modo '{mode}' não reconhecido. Use 'maior' ou 'menor'"}
            
            # Calcula as notas da escala
            scale_notes = [self.note_names[(tonic_index + interval) % 12] for interval in intervals]
            
            # Constrói informações dos acordes
            chords = []
            functions = self.chord_functions.get(mode_lower.replace("maior", "major").replace("menor", "minor"), {})
            
            for i, (note, quality, roman) in enumerate(zip(scale_notes, chord_qualities, roman_numerals)):
                degree = i + 1
                chord_name = note + quality
                
                function_info = functions.get(degree, {})
                
                chord_info = {
                    "grau": roman,
                    "acorde": chord_name,
                    "cifra": chord_name,
                    "funcao": function_info.get("function", "Função não definida"),
                    "descricao": function_info.get("description", ""),
                    "tensao": function_info.get("tension", "Não definida"),
                    "notas": self.get_triad_notes(note, quality if quality else "major")
                }
                
                chords.append(chord_info)
            
            # Progressões comuns para este modo
            progressions = self.common_progressions.get(
                mode_lower.replace("maior", "major").replace("menor", "minor"), 
                {}
            )
            
            # Substitutos harmônicos
            substitutes = self.get_harmonic_substitutes(tonic, mode_lower)
            
            result = {
                "tonalidade": f"{tonic} {mode_name}",
                "acordes": chords,
                "escala": scale_notes,
                "descricao": f"O campo harmônico {mode_name} oferece uma paleta completa de acordes para composição e improvisação.",
                "progressoes_comuns": [f"{name}: {' - '.join(prog)}" for name, prog in progressions.items()],
                "centros_tonais": self.get_tonal_centers(mode_lower),
                "substitutos_harmonicos": substitutes,
                "cadencias": self.get_cadences(mode_lower)
            }
            
            logger.info(f"Campo harmônico explicado: {tonic} {mode}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao explicar campo harmônico: {str(e)}")
            return {"erro": f"Erro interno: {str(e)}"}
    
    def explain_interval(self, note1: str, note2: str) -> Dict[str, Any]:
        """Explica o intervalo entre duas notas com informações detalhadas."""
        try:
            logger.info(f"Explicando intervalo: {note1} para {note2}")
            
            note1, note2 = note1.upper(), note2.upper()
            
            if note1 not in self.note_names or note2 not in self.note_names:
                return {"erro": "Uma ou ambas as notas não são válidas"}
            
            idx1 = self.note_names.index(note1)
            idx2 = self.note_names.index(note2)
            
            # Calcula intervalo ascendente
            interval = (idx2 - idx1) % 12
            
            interval_info = self.intervals[interval]
            
            result = {
                "nota1": note1,
                "nota2": note2,
                "intervalo": interval_info["name"],
                "qualidade": interval_info["quality"],
                "semitons": interval,
                "descricao": self.get_interval_description(interval),
                "exemplo_musical": self.interval_examples.get(interval, "Exemplo não disponível"),
                "consonancia": self.get_consonance_info(interval),
                "tensao_harmonica": self.get_interval_tension(interval),
                "uso_melodico": self.get_melodic_usage(interval),
                "intervalo_complementar": self.get_complementary_interval(interval)
            }
            
            logger.info(f"Intervalo explicado: {note1} para {note2}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao explicar intervalo: {str(e)}")
            return {"erro": f"Erro interno: {str(e)}"}
    
    def explain_mode(self, tonic: str, mode_name: str) -> Dict[str, Any]:
        """Explica um modo musical com informações detalhadas."""
        try:
            logger.info(f"Explicando modo: {tonic} {mode_name}")
            
            tonic = tonic.upper()
            mode_name = mode_name.lower()
            
            if tonic not in self.note_names:
                return {"erro": f"Nota '{tonic}' não reconhecida"}
            
            if mode_name not in self.modes:
                available = ", ".join(self.modes.keys())
                return {"erro": f"Modo '{mode_name}' não reconhecido. Disponíveis: {available}"}
            
            tonic_index = self.note_names.index(tonic)
            mode_info = self.modes[mode_name]
            
            # Calcula as notas do modo
            mode_notes = [self.note_names[(tonic_index + interval) % 12] 
                         for interval in mode_info["intervals"]]
            
            # Campo harmônico do modo
            harmonic_field = self.get_modal_harmonic_field(tonic, mode_name)
            
            result = {
                "modo": f"{tonic} {mode_name.capitalize()}",
                "notas": mode_notes,
                "intervalos": mode_info["intervals"],
                "padrao": mode_info["pattern"],
                "descricao": mode_info["description"],
                "caracteristica": mode_info["characteristic"],
                "generos_musicais": mode_info["genres"],
                "clima": mode_info["mood"],
                "acordes_caracteristicos": harmonic_field,
                "escala_parente": self.get_parent_scale(tonic, mode_name),
                "progressoes_tipicas": self.get_modal_progressions(mode_name)
            }
            
            logger.info(f"Modo explicado: {tonic} {mode_name}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao explicar modo: {str(e)}")
            return {"erro": f"Erro interno: {str(e)}"}
    
    # Métodos auxiliares
    
    def get_chord_intervals_and_info(self, chord_type: str) -> Dict[str, Any]:
        """Retorna intervalos e informações para diferentes tipos de acordes."""
        chord_types = {
            "major": {
                "intervals": [0, 4, 7],
                "symbol": "",
                "description": "Acorde maior: som alegre e estável. Base da harmonia tonal.",
                "function": "Tônica, Subdominante ou Dominante",
                "tension": "Baixa (consonante)",
                "common_use": "Resolução, estabilidade harmônica"
            },
            "minor": {
                "intervals": [0, 3, 7],
                "symbol": "m",
                "description": "Acorde menor: som melancólico e introspectivo.",
                "function": "Tônica, Subdominante ou relativa menor",
                "tension": "Baixa (consonante)",
                "common_use": "Expressão melancólica, contraste com maiores"
            },
            "7": {
                "intervals": [0, 4, 7, 10],
                "symbol": "7",
                "description": "Acorde de 7ª dominante: cria tensão que pede resolução.",
                "function": "Dominante (V7)",
                "tension": "Alta (dissonante)",
                "common_use": "Cadências, blues, jazz"
            },
            "maj7": {
                "intervals": [0, 4, 7, 11],
                "symbol": "maj7",
                "description": "Acorde maior com 7ª maior: som sofisticado e jazzy.",
                "function": "Tônica (Imaj7)",
                "tension": "Média (coloração)",
                "common_use": "Jazz, bossa nova, música sofisticada"
            },
            "m7": {
                "intervals": [0, 3, 7, 10],
                "symbol": "m7",
                "description": "Acorde menor com 7ª menor: som suave e jazzy.",
                "function": "ii7, iii7, vi7",
                "tension": "Baixa-Média",
                "common_use": "Jazz, progressões ii-V-I"
            },
            "dim": {
                "intervals": [0, 3, 6],
                "symbol": "°",
                "description": "Acorde diminuto: muito instável, pede resolução.",
                "function": "Dominante substituto",
                "tension": "Muito alta",
                "common_use": "Passagem, tensão harmônica"
            },
            "aug": {
                "intervals": [0, 4, 8],
                "symbol": "+",
                "description": "Acorde aumentado: som misterioso e instável.",
                "function": "Cromático",
                "tension": "Alta",
                "common_use": "Impressionismo, passagens cromáticas"
            }
        }
        
        chord_type = chord_type.replace("maior", "major").replace("menor", "minor")
        
        if chord_type not in chord_types:
            return {"erro": f"Tipo de acorde '{chord_type}' não reconhecido"}
        
        return chord_types[chord_type]
    
    def get_scale_chord_qualities(self, scale_type: str) -> List[str]:
        """Retorna as qualidades dos acordes para uma escala."""
        if scale_type in ["major", "maior"]:
            return ["", "m", "m", "", "", "m", "dim"]
        elif scale_type in ["minor", "menor", "natural_minor"]:
            return ["m", "dim", "", "m", "m", "", ""]
        elif scale_type == "harmonic_minor":
            return ["m", "dim", "aug", "m", "", "", "dim"]
        elif scale_type == "melodic_minor":
            return ["m", "m", "aug", "", "", "dim", "dim"]
        else:
            return [""] * 7
    
    def get_related_modes(self, tonic: str) -> Dict[str, str]:
        """Retorna os modos relacionados a uma escala maior."""
        modes_order = ["jônio", "dórico", "frígio", "lídio", "mixolídio", "eólio", "lócrio"]
        tonic_index = self.note_names.index(tonic)
        
        related_modes = {}
        for i, mode in enumerate(modes_order):
            mode_tonic = self.note_names[(tonic_index + i) % 12]
            related_modes[mode] = f"{mode_tonic} {mode}"
        
        return related_modes
    
    def get_triad_notes(self, root: str, quality: str) -> List[str]:
        """Retorna as notas de uma tríade."""
        root_index = self.note_names.index(root)
        
        if quality in ["major", ""]:
            intervals = [0, 4, 7]
        elif quality in ["minor", "m"]:
            intervals = [0, 3, 7]
        elif quality == "dim":
            intervals = [0, 3, 6]
        elif quality == "aug":
            intervals = [0, 4, 8]
        else:
            intervals = [0, 4, 7]  # Padrão maior
        
        return [self.note_names[(root_index + interval) % 12] for interval in intervals]
    
    def get_harmonic_substitutes(self, tonic: str, mode: str) -> Dict[str, List[str]]:
        """Retorna substitutos harmônicos comuns."""
        if mode in ["major", "maior"]:
            return {
                "Tônica": ["vi", "iii", "I"],
                "Subdominante": ["ii", "IV", "vi"],
                "Dominante": ["V", "vii°", "iii"]
            }
        else:
            return {
                "Tônica": ["i", "III", "VI"],
                "Subdominante": ["iv", "ii°", "VI"],
                "Dominante": ["v", "V", "VII"]
            }
    
    def get_tonal_centers(self, mode: str) -> List[str]:
        """Retorna centros tonais importantes."""
        if mode in ["major", "maior"]:
            return ["I (tônica)", "V (dominante)", "vi (relativa menor)"]
        else:
            return ["i (tônica)", "III (relativa maior)", "v (dominante menor)"]
    
    def get_cadences(self, mode: str) -> Dict[str, str]:
        """Retorna cadências importantes."""
        if mode in ["major", "maior"]:
            return {
                "Autêntica": "V - I",
                "Plagal": "IV - I", 
                "Meio cadência": "I - V",
                "Deceptiva": "V - vi"
            }
        else:
            return {
                "Menor autêntica": "V - i",
                "Plagal menor": "iv - i",
                "Frigia": "ii° - i",
                "Andaluza": "VII - VI - V - i"
            }
    
    def get_modal_harmonic_field(self, tonic: str, mode_name: str) -> List[str]:
        """Retorna campo harmônico modal."""
        tonic_index = self.note_names.index(tonic)
        mode_intervals = self.modes[mode_name]["intervals"]
        
        # Gera acordes modais básicos
        chords = []
        for i in range(len(mode_intervals)):
            chord_root = self.note_names[(tonic_index + mode_intervals[i]) % 12]
            # Simplificação: assume tríades maiores nos graus 1, 4, 5
            if i in [0, 3, 4]:
                chords.append(chord_root)
            else:
                chords.append(chord_root + "m")
        
        return chords
    
    def get_parent_scale(self, tonic: str, mode_name: str) -> str:
        """Retorna a escala pai do modo."""
        mode_to_degree = {
            "jônio": 0, "dórico": 1, "frígio": 2, "lídio": 3,
            "mixolídio": 4, "eólio": 5, "lócrio": 6
        }
        
        if mode_name not in mode_to_degree:
            return "Escala pai não determinada"
        
        degree = mode_to_degree[mode_name]
        tonic_index = self.note_names.index(tonic)
        parent_tonic_index = (tonic_index - degree * 2) % 12  # Aproximação
        parent_tonic = self.note_names[parent_tonic_index]
        
        return f"{parent_tonic} maior"
    
    def get_modal_progressions(self, mode_name: str) -> List[str]:
        """Retorna progressões típicas do modo."""
        modal_progressions = {
            "dórico": ["i - IV - i", "i - VII - i", "i - iv - VII - i"],
            "frígio": ["i - bII - i", "i - VII - VI - VII"],
            "lídio": ["I - II - I", "I - vii° - I"],
            "mixolídio": ["I - VII - I", "I - v - IV - I"],
            "eólio": ["i - VII - VI - VII", "i - iv - v - i"],
            "lócrio": ["i° - bII - i°", "i° - bV - i°"]
        }
        
        return modal_progressions.get(mode_name, ["Progressões não definidas"])
    
    def suggest_chord_progression(self, root: str, chord_type: str) -> str:
        """Sugere uma progressão que inclui o acorde dado."""
        progressions = [
            f"{root} - F - C - G",
            f"Am - {root} - F - G", 
            f"{root} - Dm - G - C",
            f"C - {root} - Am - F",
            f"{root} - G - Am - F"
        ]
        return random.choice(progressions)
    
    def get_chord_inversions(self, chord_notes: List[str]) -> Dict[str, List[str]]:
        """Retorna as inversões de um acorde."""
        inversions = {
            "Fundamental": chord_notes,
            "1ª inversão": chord_notes[1:] + [chord_notes[0]],
            "2ª inversão": chord_notes[2:] + chord_notes[:2] if len(chord_notes) >= 3 else chord_notes
        }
        
        if len(chord_notes) >= 4:
            inversions["3ª inversão"] = chord_notes[3:] + chord_notes[:3]
        
        return inversions
    
    def get_interval_description(self, semitones: int) -> str:
        """Retorna descrição detalhada de um intervalo."""
        descriptions = {
            0: "Mesmo som, sem diferença de altura. Base para afinação.",
            1: "Intervalo muito dissonante, cria forte tensão harmônica.",
            2: "Intervalo consonante, som suave. Muito usado em melodias.",
            3: "Característico de acordes menores, expressa melancolia.",
            4: "Característico de acordes maiores, expressa alegria.",
            5: "Intervalo muito estável, fundamento da harmonia ocidental.",
            6: "Intervalo muito dissonante, divide a oitava. Usado para tensão.",
            7: "Intervalo perfeito, muito consonante. Base de acordes.",
            8: "Intervalo suave, usado em melodias e harmonizações.",
            9: "Intervalo brilhante, comum em acordes maiores.",
            10: "Usado em acordes de 7ª, cria tensão moderada.",
            11: "Intervalo muito consonante, sofisticado no jazz.",
            12: "Repetição da nota fundamental uma oitava acima."
        }
        return descriptions.get(semitones, "Descrição não disponível.")
    
    def get_consonance_info(self, semitones: int) -> str:
        """Retorna informação sobre consonância do intervalo."""
        consonant = [0, 3, 4, 5, 7, 8, 9, 12]
        dissonant = [1, 2, 6, 10, 11]
        
        if semitones in consonant:
            return "Consonante"
        elif semitones in dissonant:
            return "Dissonante"
        else:
            return "Neutro"
    
    def get_interval_tension(self, semitones: int) -> str:
        """Retorna nível de tensão harmônica do intervalo."""
        tension_levels = {
            0: "Nenhuma", 1: "Muito alta", 2: "Baixa", 3: "Baixa",
            4: "Muito baixa", 5: "Nenhuma", 6: "Máxima", 7: "Nenhuma",
            8: "Baixa", 9: "Muito baixa", 10: "Média", 11: "Baixa", 12: "Nenhuma"
        }
        return tension_levels.get(semitones, "Não definida")
    
    def get_melodic_usage(self, semitones: int) -> str:
        """Retorna uso melódico comum do intervalo."""
        usages = {
            1: "Passagem cromática, appoggiatura",
            2: "Graus conjuntos, melodias suaves",
            3: "Expressão melancólica, blues",
            4: "Melodias alegres, fanfarras", 
            5: "Saltos melódicos estáveis",
            7: "Saltos melódicos, arpejos",
            8: "Melodias expressivas",
            9: "Melodias brilhantes",
            12: "Mudança de registro"
        }
        return usages.get(semitones, "Uso variado")
    
    def get_complementary_interval(self, semitones: int) -> str:
        """Retorna o intervalo complementar (soma = oitava)."""
        complement = (12 - semitones) % 12
        return self.intervals[complement]["name"] if complement in self.intervals else "N/A"

# Função para gerar exercícios aprimorada
def generate_exercise(exercise_type: str) -> Dict[str, Any]:
    """Gera exercícios de teoria musical mais elaborados."""
    try:
        teacher = MusicTheoryTeacher()
        
        if exercise_type == "interval":
            return generate_interval_exercise(teacher)
        elif exercise_type == "chord": 
            return generate_chord_exercise(teacher)
        elif exercise_type == "scale":
            return generate_scale_exercise(teacher)
        elif exercise_type == "progression":
            return generate_progression_exercise(teacher)
        elif exercise_type == "mode":
            return generate_mode_exercise(teacher)
        else:
            return {"erro": f"Tipo de exercício '{exercise_type}' não reconhecido"}
            
    except Exception as e:
        logger.error(f"Erro ao gerar exercício: {str(e)}")
        return {"erro": f"Erro interno: {str(e)}"}

def generate_interval_exercise(teacher: MusicTheoryTeacher) -> Dict[str, Any]:
    """Gera exercício de intervalos."""
    note1 = random.choice(teacher.note_names)
    note2 = random.choice(teacher.note_names)
    answer = teacher.explain_interval(note1, note2)
    
    # Diferentes tipos de pergunta
    question_types = [
        f"Qual é o intervalo entre {note1} e {note2}?",
        f"Quantos semitons há entre {note1} e {note2}?",
        f"O intervalo {note1}-{note2} é consonante ou dissonante?"
    ]
    
    return {
        "tipo": "Identificação de Intervalo",
        "pergunta": random.choice(question_types),
        "resposta": answer,
        "nivel": "Básico"
    }

def generate_chord_exercise(teacher: MusicTheoryTeacher) -> Dict[str, Any]:
    """Gera exercício de acordes."""
    root = random.choice(teacher.note_names)
    chord_types = ["major", "minor", "7", "maj7"]
    chord_type = random.choice(chord_types)
    answer = teacher.explain_chord(root, chord_type)
    
    type_names = {"major": "maior", "minor": "menor", "7": "7", "maj7": "maj7"}
    
    return {
        "tipo": "Formação de Acorde", 
        "pergunta": f"Quais são as notas do acorde {root} {type_names.get(chord_type, chord_type)}?",
        "resposta": answer,
        "nivel": "Intermediário"
    }

def generate_scale_exercise(teacher: MusicTheoryTeacher) -> Dict[str, Any]:
    """Gera exercício de escalas."""
    tonic = random.choice(teacher.note_names)
    scale_types = ["major", "minor"]
    scale_type = random.choice(scale_types)
    answer = teacher.explain_scale(tonic, scale_type)
    
    return {
        "tipo": "Escala Musical",
        "pergunta": f"Quais são as notas da escala de {tonic} {'maior' if scale_type == 'major' else 'menor'}?",
        "resposta": answer,
        "nivel": "Básico"
    }

def generate_progression_exercise(teacher: MusicTheoryTeacher) -> Dict[str, Any]:
    """Gera exercício de progressões."""
    tonic = random.choice(teacher.note_names)
    mode = random.choice(["major", "minor"])
    harmonic_field = teacher.explain_harmonic_field(tonic, mode)
    
    return {
        "tipo": "Campo Harmônico",
        "pergunta": f"Qual é o campo harmônico de {tonic} {'maior' if mode == 'major' else 'menor'}?",
        "resposta": harmonic_field,
        "nivel": "Avançado"
    }

def generate_mode_exercise(teacher: MusicTheoryTeacher) -> Dict[str, Any]:
    """Gera exercício de modos."""
    tonic = random.choice(teacher.note_names)
    modes = ["dórico", "frígio", "lídio", "mixolídio"]
    mode = random.choice(modes)
    answer = teacher.explain_mode(tonic, mode)
    
    return {
        "tipo": "Modo Musical",
        "pergunta": f"Quais são as características do modo {tonic} {mode}?",
        "resposta": answer,
        "nivel": "Avançado"
    }