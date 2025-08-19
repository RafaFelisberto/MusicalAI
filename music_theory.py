import music21 as m21
from typing import List, Dict, Tuple
import random

class MusicTheoryTeacher:
    """Classe para ensino avançado de teoria musical."""
    
    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.intervals = {
            0: "Uníssono",
            1: "2ª menor",
            2: "2ª maior", 
            3: "3ª menor",
            4: "3ª maior",
            5: "4ª justa",
            6: "Trítono",
            7: "5ª justa",
            8: "6ª menor",
            9: "6ª maior",
            10: "7ª menor",
            11: "7ª maior",
            12: "Oitava"
        }
        
        self.modes = {
            "jônio": [0, 2, 4, 5, 7, 9, 11],
            "dórico": [0, 2, 3, 5, 7, 9, 10],
            "frígio": [0, 1, 3, 5, 7, 8, 10],
            "lídio": [0, 2, 4, 6, 7, 9, 11],
            "mixolídio": [0, 2, 4, 5, 7, 9, 10],
            "eólio": [0, 2, 3, 5, 7, 8, 10],
            "lócrio": [0, 1, 3, 5, 6, 8, 10],
            "pentatônica maior": [0, 2, 4, 7, 9],
            "pentatônica menor": [0, 3, 5, 7, 10],
            "blues": [0, 3, 5, 6, 7, 10]
        }
        
        # Cadências harmônicas expandidas
        self.cadences = {
            "autêntica perfeita": {
                "progressao": "V - I",
                "descricao": "A cadência autêntica perfeita é a mais forte e conclusiva.",
                "funcao": "Conclusiva, forte senso de repouso.",
                "exemplos": ["G - C em C maior", "E - Am em A menor"]
            },
            "plagal": {
                "progressao": "IV - I",
                "descricao": "Conhecida como 'Amém' cadência, é menos conclusiva que a autêntica.",
                "funcao": "Conclusiva, mas suave e menos final.",
                "exemplos": ["F - C em C maior", "D - A em A maior"]
            },
            "deceptiva": {
                "progressao": "V - vi (ou VI)",
                "descricao": "O acorde de dominante não resolve na tônica, criando surpresa.",
                "funcao": "Evita a conclusão esperada, cria surpresa.",
                "exemplos": ["G - Am em C maior", "E - F em A menor"]
            }
        }
    
    def explain_scale(self, tonic: str, scale_type: str = "major") -> Dict:
        """Explica uma escala musical com análise detalhada."""
        try:
            if scale_type.lower() == "major" or scale_type.lower() == "maior":
                scale = m21.scale.MajorScale(tonic)
                pattern = "T-T-S-T-T-T-S"
                description = "A escala maior tem um som alegre e brilhante."
            elif scale_type.lower() == "minor" or scale_type.lower() == "menor":
                scale = m21.scale.MinorScale(tonic)
                pattern = "T-S-T-T-S-T-T"
                description = "A escala menor natural tem um som melancólico e introspectivo."
            else:
                return {"erro": "Tipo de escala não reconhecido. Use 'maior' ou 'menor'."}
            
            notes = [str(p) for p in scale.getPitches(tonic, tonic + '8')]
            
            return {
                "escala": f"{tonic} {scale_type}",
                "notas": notes,
                "padrao": pattern,
                "descricao": description
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    def explain_chord(self, root: str, chord_type: str = "major") -> Dict:
        """Explica a formação de um acorde com análise detalhada."""
        try:
            root_idx = self.note_names.index(root.upper())
            
            if chord_type.lower() in ["major", "maior", "M"]:
                intervals = [0, 4, 7]
                chord_notes = [self.note_names[(root_idx + i) % 12] for i in intervals]
                description = "Acorde maior: som alegre e estável. Formado por 1ª + 3ª maior + 5ª justa."
                
            elif chord_type.lower() in ["minor", "menor", "m"]:
                intervals = [0, 3, 7]
                chord_notes = [self.note_names[(root_idx + i) % 12] for i in intervals]
                description = "Acorde menor: som melancólico e introspectivo. Formado por 1ª + 3ª menor + 5ª justa."
                
            elif chord_type.lower() in ["7", "dominant7", "dominante"]:
                intervals = [0, 4, 7, 10]
                chord_notes = [self.note_names[(root_idx + i) % 12] for i in intervals]
                description = "Acorde de 7ª dominante: cria tensão que resolve no acorde seguinte."
            else:
                return {"erro": "Tipo de acorde não reconhecido."}
            
            interval_names = [self.intervals[i] for i in intervals]
            
            return {
                "acorde": f"{root.upper()}{chord_type}",
                "notas": chord_notes,
                "intervalos": interval_names,
                "descricao": description,
                "exemplo_progressao": self.suggest_chord_progression(root.upper(), chord_type)
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    def explain_interval(self, note1: str, note2: str) -> Dict:
        """Explica o intervalo entre duas notas."""
        try:
            idx1 = self.note_names.index(note1.upper())
            idx2 = self.note_names.index(note2.upper())
            
            # Calcula o intervalo ascendente
            interval = (idx2 - idx1) % 12
            
            return {
                "nota1": note1.upper(),
                "nota2": note2.upper(),
                "intervalo": self.intervals[interval],
                "semitons": interval,
                "descricao": self.get_interval_description(interval),
                "exemplo_musical": self.get_interval_example(interval)
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    def get_interval_description(self, semitones: int) -> str:
        """Retorna descrição de um intervalo."""
        descriptions = {
            0: "Mesmo som, sem diferença de altura.",
            1: "Intervalo muito dissonante, cria tensão.",
            2: "Intervalo consonante, som suave.",
            3: "Característico de acordes menores, som melancólico.",
            4: "Característico de acordes maiores, som alegre.",
            5: "Intervalo muito estável, base da harmonia.",
            6: "Intervalo muito dissonante, divide a oitava ao meio.",
            7: "Intervalo perfeito, muito consonante.",
            8: "Intervalo suave, usado em melodias.",
            9: "Intervalo brilhante, usado em acordes maiores.",
            10: "Usado em acordes de 7ª, cria tensão moderada.",
            11: "Intervalo muito consonante, usado em acordes sofisticados.",
            12: "Repetição da nota fundamental uma oitava acima."
        }
        return descriptions.get(semitones, "Descrição não disponível.")
    
    def get_interval_example(self, semitones: int) -> str:
        """Retorna exemplo musical de um intervalo."""
        examples = {
            0: "Duas vozes cantando a mesma nota",
            1: "Tema do filme 'Tubarão'",
            2: "Início de 'Frère Jacques'",
            3: "Início de 'Greensleeves'",
            4: "Início de 'When the Saints Go Marching In'",
            5: "Início de 'Here Comes the Bride'",
            6: "Abertura de 'West Side Story' (Maria)",
            7: "Início de 'Twinkle, Twinkle, Little Star'",
            8: "Tema de 'The Way You Look Tonight'",
            9: "Início de 'My Bonnie Lies Over the Ocean'",
            10: "Acorde dominante em 'Happy Birthday'",
            11: "Início de 'Take On Me' (a-ha)",
            12: "Início de 'Somewhere Over the Rainbow'"
        }
        return examples.get(semitones, "Exemplo não disponível.")
    
    def explain_mode(self, tonic: str, mode_name: str) -> Dict:
        """Explica um modo musical."""
        try:
            mode_name_lower = mode_name.lower()
            if mode_name_lower not in self.modes:
                return {"erro": f"Modo '{mode_name}' não reconhecido."}
            
            root_idx = self.note_names.index(tonic.upper())
            intervals = self.modes[mode_name_lower]
            notes = [self.note_names[(root_idx + i) % 12] for i in intervals]
            
            mode_descriptions = {
                "jônio": "Modo maior tradicional, alegre e estável.",
                "dórico": "Modo menor com 6ª maior, usado no jazz e folk.",
                "frígio": "Modo menor com 2ª menor, som espanhol/flamenco.",
                "lídio": "Modo maior com 4ª aumentada, som etéreo.",
                "mixolídio": "Modo maior com 7ª menor, usado no rock e blues.",
                "eólio": "Modo menor natural, melancólico.",
                "lócrio": "Modo com 5ª diminuta, muito instável."
            }
            
            mode_genres = {
                "jônio": ["Pop", "Rock", "Clássica"],
                "dórico": ["Jazz", "Folk", "Rock progressivo"],
                "frígio": ["Flamenco", "Metal", "Música espanhola"],
                "lídio": ["Jazz fusion", "Trilhas sonoras", "Música new age"],
                "mixolídio": ["Blues", "Rock", "Country"],
                "eólio": ["Rock", "Pop", "Folk"],
                "lócrio": ["Jazz", "Metal extremo", "Música experimental"]
            }
            
            return {
                "modo": f"{tonic.upper()} {mode_name}",
                "notas": notes,
                "caracteristica": self.get_mode_characteristic(mode_name_lower),
                "descricao": mode_descriptions.get(mode_name_lower, "Descrição não disponível."),
                "generos_musicais": mode_genres.get(mode_name_lower, [])
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    def get_mode_characteristic(self, mode_name: str) -> str:
        """Retorna a característica principal de um modo."""
        characteristics = {
            "jônio": "3ª e 7ª maiores",
            "dórico": "3ª menor, 6ª maior",
            "frígio": "2ª menor, 3ª menor",
            "lídio": "4ª aumentada",
            "mixolídio": "3ª maior, 7ª menor",
            "eólio": "3ª menor, 6ª menor, 7ª menor",
            "lócrio": "2ª menor, 5ª diminuta"
        }
        return characteristics.get(mode_name, "Característica não definida.")
    
    def explain_cadence(self, cadence_type: str) -> Dict:
        """Explica uma cadência harmônica."""
        cadence_type_lower = cadence_type.lower()
        
        # Busca por palavras-chave
        if "autêntica" in cadence_type_lower or "autentica" in cadence_type_lower:
            cadence_key = "autêntica perfeita"
        elif "plagal" in cadence_type_lower:
            cadence_key = "plagal"
        elif "deceptiva" in cadence_type_lower:
            cadence_key = "deceptiva"
        else:
            return {"erro": f"Cadência '{cadence_type}' não reconhecida."}
        
        if cadence_key in self.cadences:
            cadence_info = self.cadences[cadence_key]
            return {
                "cadencia": cadence_key,
                "progressao": cadence_info["progressao"],
                "descricao": cadence_info["descricao"],
                "funcao": cadence_info["funcao"]
            }
        
        return {"erro": f"Cadência '{cadence_type}' não encontrada."}
    
    def explain_harmonic_function(self, degree: str, mode: str) -> Dict:
        """Explica a função harmônica de um grau."""
        try:
            degree_num = self.roman_to_number(degree)
            
            if "maior" in mode.lower():
                functions = {
                    1: {"nome": "Tônica", "descricao": "Centro tonal, repouso", "exemplos": ["C em C maior"]},
                    2: {"nome": "Supertônica", "descricao": "Preparação subdominante", "exemplos": ["Dm em C maior"]},
                    3: {"nome": "Mediante", "descricao": "Tônica relativa", "exemplos": ["Em em C maior"]},
                    4: {"nome": "Subdominante", "descricao": "Afastamento da tônica", "exemplos": ["F em C maior"]},
                    5: {"nome": "Dominante", "descricao": "Tensão máxima", "exemplos": ["G em C maior"]},
                    6: {"nome": "Superdominante", "descricao": "Tônica relativa", "exemplos": ["Am em C maior"]},
                    7: {"nome": "Sensível", "descricao": "Tensão dominante", "exemplos": ["Bdim em C maior"]}
                }
            else:
                functions = {
                    1: {"nome": "Tônica", "descricao": "Centro tonal, repouso", "exemplos": ["Am em A menor"]},
                    2: {"nome": "Supertônica", "descricao": "Preparação subdominante", "exemplos": ["Bdim em A menor"]},
                    3: {"nome": "Mediante", "descricao": "Dominante relativa", "exemplos": ["C em A menor"]},
                    4: {"nome": "Subdominante", "descricao": "Afastamento da tônica", "exemplos": ["Dm em A menor"]},
                    5: {"nome": "Dominante", "descricao": "Tensão máxima", "exemplos": ["Em em A menor"]},
                    6: {"nome": "Superdominante", "descricao": "Subdominante relativa", "exemplos": ["F em A menor"]},
                    7: {"nome": "Subtônica", "descricao": "Dominante relativa", "exemplos": ["G em A menor"]}
                }
            
            if degree_num in functions:
                func_info = functions[degree_num]
                return {
                    "grau": degree,
                    "modo": mode,
                    "nome": func_info["nome"],
                    "descricao": func_info["descricao"],
                    "exemplos": func_info["exemplos"]
                }
            else:
                return {"erro": f"Grau '{degree}' não reconhecido."}
                
        except Exception as e:
            return {"erro": str(e)}
    
    def roman_to_number(self, roman: str) -> int:
        """Converte numeral romano para número."""
        roman_map = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
            'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7
        }
        return roman_map.get(roman.strip(), 1)
    
    def explain_harmonic_field(self, tonic: str, mode: str = "major") -> Dict:
        """Explica o campo harmônico de uma tonalidade."""
        try:
            if mode.lower() in ["major", "maior"]:
                key = m21.key.Key(tonic, 'major')
                chord_qualities = ["", "m", "m", "", "", "m", "dim"]
                description = "Campo harmônico maior: base para a maioria das progressões na música ocidental."
            elif mode.lower() in ["minor", "menor"]:
                key = m21.key.Key(tonic, 'minor')
                chord_qualities = ["m", "dim", "", "m", "m", "", ""]
                description = "Campo harmônico menor: oferece sonoridades mais melancólicas e dramáticas."
            else:
                return {"erro": "Modo não reconhecido. Use 'maior' ou 'menor'."}
            
            chords = []
            roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
            
            for degree in range(1, 8):
                chord = key.getChord(degree)
                chord_name = chord.commonName
                chords.append({
                    "grau": roman_numerals[degree-1],
                    "acorde": chord_name,
                    "cifra": f"{chord.root().name}{chord_qualities[degree-1]}",
                    "funcao": self.get_chord_function(degree, mode)
                })
            
            return {
                "tonalidade": f"{tonic} {mode}",
                "acordes": chords,
                "descricao": description,
                "progressoes_comuns": self.get_common_progressions(mode)
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    def get_chord_function(self, degree: int, mode: str) -> str:
        """Retorna a função harmônica de um grau."""
        if mode.lower() in ["major", "maior"]:
            functions = {
                1: "Tônica (repouso)",
                2: "Subdominante (preparação)",
                3: "Tônica relativa",
                4: "Subdominante (afastamento)",
                5: "Dominante (tensão)",
                6: "Superdominante (tônica relativa)",
                7: "Meio diminuto (Tensão)"
            }

class generate_exercise:
    def __init__(self, music_theory: MusicTheoryTeacher):
        self.music_theory = music_theory

    def create_chord_progression_exercise(self, tonic: str, mode: str) -> Dict:
        """Cria um exercício de progressão de acordes."""
        harmonic_field = self.music_theory.explain_harmonic_field(tonic, mode)
        if "erro" in harmonic_field:
            return {"erro": harmonic_field["erro"]}

        chords = harmonic_field["acordes"]
        progression = random.sample(chords, 4)  # Seleciona 4 acordes aleatórios

        return {
            "tonalidade": harmonic_field["tonalidade"],
            "progressoes": [chord["cifra"] for chord in progression]
        }
    