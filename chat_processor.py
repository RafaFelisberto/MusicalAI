import re
import logging
from typing import Dict, List, Optional, Any
from music_theory import MusicTheoryTeacher

logger = logging.getLogger(__name__)

class ChatProcessor:
    """Processador de mensagens do chat musical."""
    
    def __init__(self, theory_teacher: MusicTheoryTeacher):
        self.theory_teacher = theory_teacher
        self.setup_patterns()
    
    def setup_patterns(self):
        """Define os padrões regex para reconhecimento de perguntas."""
        self.patterns = {
            'campo_harmonico': re.compile(
                r'campo harm[oô]nico.*?(?:de\s+)?([a-g]#?)\s*(maior|menor)?',
                re.IGNORECASE
            ),
            'escala': re.compile(
                r'escala.*?(?:de\s+)?([a-g]#?)\s*(maior|menor)?',
                re.IGNORECASE
            ),
            'acorde': re.compile(
                r'(?:acorde\s+)?([a-g]#?)\s*(maior|menor|m|7|maj7|dim|aug)?',
                re.IGNORECASE
            ),
            'intervalo': re.compile(
                r'intervalo.*?entre\s+([a-g]#?)\s+e\s+([a-g]#?)',
                re.IGNORECASE
            ),
            'modo': re.compile(
                r'(?:modo\s+)?([a-g]#?)\s*(j[oô]nio|d[oó]rico|fr[ií]gio|l[ií]dio|mixol[ií]dio|e[oó]lio|l[oó]crio)',
                re.IGNORECASE
            ),
            'formacao_acorde': re.compile(
                r'(?:como\s+formar|forma[çc][aã]o.*?do?)\s+(?:acorde\s+)?([a-g]#?)\s*(maior|menor|m|7)?',
                re.IGNORECASE
            )
        }
    
    def process_message(self, message: str) -> str:
        """Processa uma mensagem e retorna a resposta."""
        try:
            message = message.strip()
            logger.info(f"Processando mensagem: {message}")
            
            # Normaliza a mensagem
            normalized_message = self.normalize_message(message)
            
            # Tenta identificar o tipo de pergunta e processar
            response = self.identify_and_process(normalized_message)
            
            if response:
                return response
            
            # Se não reconheceu nenhum padrão, retorna mensagem padrão
            return self.get_default_response()
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente."
    
    def normalize_message(self, message: str) -> str:
        """Normaliza a mensagem para melhor processamento."""
        # Remove acentos e caracteres especiais desnecessários
        replacements = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i', 'î': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u', 'û': 'u',
            'ç': 'c'
        }
        
        normalized = message.lower()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized
    
    def identify_and_process(self, message: str) -> Optional[str]:
        """Identifica o tipo de pergunta e processa adequadamente."""
        
        # Campo harmônico
        if 'campo harmonico' in message or 'campo harmônico' in message:
            return self.process_harmonic_field_question(message)
        
        # Escala
        if 'escala' in message:
            return self.process_scale_question(message)
        
        # Formação de acorde
        if any(phrase in message for phrase in ['como formar', 'formacao', 'formação']):
            return self.process_chord_formation_question(message)
        
        # Acorde específico
        if 'acorde' in message or self.is_chord_query(message):
            return self.process_chord_question(message)
        
        # Intervalo
        if 'intervalo' in message and 'entre' in message:
            return self.process_interval_question(message)
        
        # Modo
        if self.is_mode_query(message):
            return self.process_mode_question(message)
        
        # Perguntas gerais
        if 'circulo' in message or 'círculo' in message or 'ciclo' in message:
            return self.get_circle_of_fifths_info()
        
        if 'exercicio' in message or 'exercício' in message:
            return self.get_exercise_info()
        
        return None
    
    def process_harmonic_field_question(self, message: str) -> str:
        """Processa perguntas sobre campo harmônico."""
        match = self.patterns['campo_harmonico'].search(message)
        
        if not match:
            return "Especifique a tonalidade. Exemplo: 'campo harmônico de C maior'"
        
        tonica = match.group(1).upper()
        modo = match.group(2) or 'maior'  # Padrão é maior
        
        mode_eng = 'minor' if 'menor' in modo.lower() else 'major'
        resultado = self.theory_teacher.explain_harmonic_field(tonica, mode_eng)
        
        if "erro" in resultado:
            return f"❌ {resultado['erro']}"
        
        # Formata a resposta
        acordes_info = []
        for acorde in resultado["acordes"]:
            acordes_info.append(f"<strong>{acorde['grau']}</strong> - {acorde['cifra']} ({acorde['funcao']})")
        
        progressoes = "<br>".join(resultado["progressoes_comuns"])
        
        return f"""
        <strong>🎼 Campo harmônico de {resultado['tonalidade']}:</strong><br><br>
        {' <br>'.join(acordes_info)}<br><br>
        <strong>📝 Progressões comuns:</strong><br>
        {progressoes}
        """
    
    def process_scale_question(self, message: str) -> str:
        """Processa perguntas sobre escalas."""
        match = self.patterns['escala'].search(message)
        
        if not match:
            return "Especifique a escala. Exemplo: 'escala de D maior'"
        
        tonica = match.group(1).upper()
        modo = match.group(2) or 'maior'
        
        scale_type = 'minor' if 'menor' in modo.lower() else 'major'
        resultado = self.theory_teacher.explain_scale(tonica, scale_type)
        
        if "erro" in resultado:
            return f"❌ {resultado['erro']}"
        
        return f"""
        <strong>🎵 Escala de {resultado['escala']}:</strong><br>
        <strong>Notas:</strong> {' - '.join(resultado['notas'])}<br>
        <strong>Padrão:</strong> {resultado['padrao']} (T=Tom, S=Semitom)<br>
        <strong>Descrição:</strong> {resultado['descricao']}
        """
    
    def process_chord_formation_question(self, message: str) -> str:
        """Processa perguntas sobre formação de acordes."""
        match = self.patterns['formacao_acorde'].search(message)
        
        if not match:
            return """
            <strong>🎸 Formação de Acordes Básicos:</strong><br><br>
            • <strong>Acorde Maior:</strong> 1ª + 3ª maior + 5ª justa<br>
            • <strong>Acorde Menor:</strong> 1ª + 3ª menor + 5ª justa<br>
            • <strong>Acorde de 7ª:</strong> Tríade + 7ª menor<br><br>
            Exemplo: "como formar acorde C maior"
            """
        
        root = match.group(1).upper()
        chord_type = match.group(2) or 'maior'
        
        # Converte para formato do theory_teacher
        if chord_type.lower() in ['menor', 'm']:
            chord_type_eng = 'minor'
        elif chord_type == '7':
            chord_type_eng = '7'
        else:
            chord_type_eng = 'major'
        
        resultado = self.theory_teacher.explain_chord(root, chord_type_eng)
        
        if "erro" in resultado:
            return f"❌ {resultado['erro']}"
        
        return f"""
        <strong>🎸 Acorde {resultado['acorde']}:</strong><br>
        <strong>Notas:</strong> {' - '.join(resultado['notas'])}<br>
        <strong>Intervalos:</strong> {', '.join(resultado['intervalos'])}<br>
        <strong>Descrição:</strong> {resultado['descricao']}<br>
        <strong>Cifra:</strong> {resultado['cifra']}
        """
    
    def process_chord_question(self, message: str) -> str:
        """Processa perguntas sobre acordes específicos."""
        match = self.patterns['acorde'].search(message)
        
        if not match:
            return "Especifique o acorde. Exemplo: 'acorde C maior' ou 'G7'"
        
        root = match.group(1).upper()
        chord_type = match.group(2) or 'maior'
        
        # Mapeamento de tipos de acorde
        type_mapping = {
            'maior': 'major',
            'menor': 'minor',
            'm': 'minor',
            '7': '7',
            'maj7': 'maj7',
            'dim': 'dim',
            'aug': 'aug'
        }
        
        chord_type_eng = type_mapping.get(chord_type.lower(), 'major')
        resultado = self.theory_teacher.explain_chord(root, chord_type_eng)
        
        if "erro" in resultado:
            return f"❌ {resultado['erro']}"
        
        return f"""
        <strong>🎸 Acorde {resultado['acorde']}:</strong><br>
        <strong>Notas:</strong> {' - '.join(resultado['notas'])}<br>
        <strong>Intervalos:</strong> {', '.join(resultado['intervalos'])}<br>
        <strong>Descrição:</strong> {resultado['descricao']}
        """
    
    def process_interval_question(self, message: str) -> str:
        """Processa perguntas sobre intervalos."""
        match = self.patterns['intervalo'].search(message)
        
        if not match:
            return "Especifique as duas notas. Exemplo: 'intervalo entre C e E'"
        
        nota1 = match.group(1).upper()
        nota2 = match.group(2).upper()
        
        resultado = self.theory_teacher.explain_interval(nota1, nota2)
        
        if "erro" in resultado:
            return f"❌ {resultado['erro']}"
        
        return f"""
        <strong>🎼 Intervalo entre {resultado['nota1']} e {resultado['nota2']}:</strong><br>
        <strong>Intervalo:</strong> {resultado['intervalo']} ({resultado['semitons']} semitons)<br>
        <strong>Descrição:</strong> {resultado['descricao']}<br>
        {f"<strong>Exemplo:</strong> {resultado['exemplo_musical']}" if 'exemplo_musical' in resultado else ""}
        """
    
    def process_mode_question(self, message: str) -> str:
        """Processa perguntas sobre modos."""
        match = self.patterns['modo'].search(message)
        
        if not match:
            return """
            <strong>🎼 Modos Gregos:</strong><br>
            Jônio, Dórico, Frígio, Lídio, Mixolídio, Eólio, Lócrio<br><br>
            Exemplo: "modo C jônio" ou "D dórico"
            """
        
        tonica = match.group(1).upper()
        modo = match.group(2).lower()
        
        # Normaliza o nome do modo
        modo_mapping = {
            'jonio': 'jônio',
            'dorico': 'dórico',
            'frigio': 'frígio',
            'lidio': 'lídio',
            'mixolidio': 'mixolídio',
            'eolio': 'eólio',
            'locrio': 'lócrio'
        }
        
        modo_normalizado = modo_mapping.get(modo, modo)
        resultado = self.theory_teacher.explain_mode(tonica, modo_normalizado)
        
        if "erro" in resultado:
            return f"❌ {resultado['erro']}"
        
        return f"""
        <strong>🎼 Modo {resultado['modo']}:</strong><br>
        <strong>Notas:</strong> {' - '.join(resultado['notas'])}<br>
        <strong>Descrição:</strong> {resultado['descricao']}<br>
        {f"<strong>Características:</strong> {resultado['caracteristica']}" if 'caracteristica' in resultado else ""}
        {f"<br><strong>Gêneros:</strong> {', '.join(resultado['generos_musicais'])}" if 'generos_musicais' in resultado else ""}
        """
    
    def is_chord_query(self, message: str) -> bool:
        """Verifica se a mensagem é uma consulta sobre acorde."""
        # Padrões simples como "C", "Am", "G7"
        simple_chord_pattern = re.compile(r'^[a-g]#?(?:m|maj|dim|aug|7|maj7|m7|dim7)?$', re.IGNORECASE)
        return bool(simple_chord_pattern.match(message.strip()))
    
    def is_mode_query(self, message: str) -> bool:
        """Verifica se a mensagem é sobre modos."""
        modos = ['jonio', 'jônio', 'dorico', 'dórico', 'frigio', 'frígio', 
                'lidio', 'lídio', 'mixolidio', 'mixolídio', 'eolio', 'eólio', 
                'locrio', 'lócrio']
        
        return any(modo in message.lower() for modo in modos)
    
    def get_circle_of_fifths_info(self) -> str:
        """Retorna informações sobre o círculo das quintas."""
        return """
        <strong>🔄 Círculo das Quintas:</strong><br><br>
        <strong>Sentido horário (sustenidos):</strong><br>
        C → G → D → A → E → B → F# → C#<br><br>
        <strong>Sentido anti-horário (bemóis):</strong><br>
        C → F → Bb → Eb → Ab → Db → Gb → Cb<br><br>
        <strong>💡 Dica:</strong> É uma ferramenta fundamental para entender relações entre tonalidades e progressões harmônicas. 
        Cada movimento no sentido horário adiciona um sustenido, no anti-horário adiciona um bemol.
        """
    
    def get_exercise_info(self) -> str:
        """Retorna informações sobre exercícios."""
        return """
        <strong>🎯 Exercícios Disponíveis:</strong><br><br>
        Use os botões na seção "Exercícios Musicais" para gerar:<br><br>
        • <strong>🎼 Intervalos</strong> - Identificação de intervalos entre notas<br>
        • <strong>🎸 Acordes</strong> - Formação e análise de acordes<br>
        • <strong>🎵 Escalas</strong> - Construção de escalas musicais<br><br>
        Os exercícios são gerados automaticamente e ajudam você a praticar e fixar o conhecimento! 📚
        """
    
    def get_default_response(self) -> str:
        """Retorna resposta padrão quando não reconhece a pergunta."""
        return """
        Ainda não sei responder essa pergunta específica, mas estou aprendendo! 🎵<br><br>
        <strong>📚 Posso ajudar com:</strong><br>
        • <strong>Escalas:</strong> "escala de D maior"<br>
        • <strong>Acordes:</strong> "acorde G7" ou "como formar C menor"<br>
        • <strong>Campo harmônico:</strong> "campo harmônico de A menor"<br>
        • <strong>Intervalos:</strong> "intervalo entre F e A"<br>
        • <strong>Modos:</strong> "modo C mixolídio"<br>
        • <strong>Teoria geral:</strong> "círculo das quintas"<br><br>
        <strong>🎯 Também posso gerar exercícios para você praticar!</strong><br>
        Use os botões na seção de exercícios ou envie um arquivo de áudio para análise.
        """
    
    def extract_note_from_text(self, text: str) -> Optional[str]:
        """Extrai uma nota musical do texto."""
        note_pattern = re.compile(r'\b([a-g]#?)\b', re.IGNORECASE)
        match = note_pattern.search(text)
        return match.group(1).upper() if match else None
    
    def extract_notes_from_text(self, text: str) -> List[str]:
        """Extrai múltiplas notas musicais do texto."""
        note_pattern = re.compile(r'\b([a-g]#?)\b', re.IGNORECASE)
        matches = note_pattern.findall(text)
        return [note.upper() for note in matches]
    
    def validate_note(self, note: str) -> bool:
        """Valida se a nota está no formato correto."""
        return note.upper() in self.theory_teacher.note_names