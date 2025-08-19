from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import music21 as m21
import os
import tempfile
from audio_analysis import AudioAnalyzer, generate_basic_chord_progression
from music_theory import MusicTheoryTeacher, generate_exercise
from audio_player import AudioPlayer

from audio_player import router as audio_router


app = FastAPI()
app.include_router(audio_router)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializa o analisador de áudio e professor de teoria
audio_analyzer = AudioAnalyzer()
theory_teacher = MusicTheoryTeacher()
audio_player = AudioPlayer()

class Pergunta(BaseModel):
    texto: str

class ExerciseRequest(BaseModel):
    tipo: str

class PlayNoteRequest(BaseModel):
    note: str
    octave: int = 4
    duration: float = 1.0

@app.get("/")
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/analisar_audio")
async def analisar_audio(file: UploadFile = File(...)):
    """Endpoint para análise de arquivos de áudio."""
    try:
        # Salva o arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Analisa o áudio
        resultado = audio_analyzer.analyze_audio_file(temp_file_path)
        
        # Remove o arquivo temporário
        os.unlink(temp_file_path)
        
        # Gera progressão de acordes se a tonalidade global foi detectada
        if "tonalidade_global" in resultado and "erro" not in resultado:
            progressao = generate_basic_chord_progression(resultado["tonalidade_global"])
            resultado["progressao_sugerida"] = progressao
        
        return {"sucesso": True, "analise": resultado}
        
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@app.post("/gerar_exercicio")
def gerar_exercicio(request: ExerciseRequest):
    """Endpoint para gerar exercícios de teoria musical."""
    try:
        exercicio = generate_exercise(request.tipo)
        return {"sucesso": True, "exercicio": exercicio}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@app.post("/tocar_nota")
def tocar_nota(request: PlayNoteRequest):
    """Endpoint para tocar uma nota musical."""
    try:
        audio_data = audio_player.generate_note(request.note, request.octave, request.duration)
        audio_file_path = audio_player.save_audio_to_file(audio_data, f"nota_{request.note}_{request.octave}")
        return {"sucesso": True, "audio_url": audio_file_path}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@app.post("/perguntar")
def perguntar(pergunta: Pergunta):
    texto = pergunta.texto.lower()

    # Respostas sobre teoria musical usando o sistema de ensino
    if "campo harmônico" in texto:
        # Extrai tonalidade da pergunta
        partes = texto.split("campo harmônico")
        if len(partes) > 1:
            tonalidade_texto = partes[1].strip()
            if "de" in tonalidade_texto:
                tonalidade_texto = tonalidade_texto.replace("de", "").strip()
            
            if "maior" in tonalidade_texto:
                tonica = tonalidade_texto.replace("maior", "").strip().upper()
                resultado = theory_teacher.explain_harmonic_field(tonica, "major")
            elif "menor" in tonalidade_texto:
                tonica = tonalidade_texto.replace("menor", "").strip().upper()
                resultado = theory_teacher.explain_harmonic_field(tonica, "minor")
            else:
                # Assume maior se não especificado
                tonica = tonalidade_texto.strip().upper()
                resultado = theory_teacher.explain_harmonic_field(tonica, "major")
            
            if "erro" in resultado:
                return {"resposta": resultado["erro"]}
            else:
                acordes_info = []
                for acorde in resultado["acordes"]:
                    acordes_info.append(f"{acorde["grau"]} - {acorde["cifra"]} ({acorde["funcao"]})")
                
                resposta = f"Campo harmônico de {resultado["tonalidade"]}:\n"
                resposta += "\n".join(acordes_info)
                resposta += f"\n\nProgressões comuns:\n" + "\n".join(resultado["progressoes_comuns"])
                return {"resposta": resposta}
        else:
            return {"resposta": "Especifique a tonalidade. Exemplo: 'campo harmônico de C maior'"}

    elif "escala de" in texto:
        # Extrai a tonalidade da pergunta
        partes = texto.split("escala de")
        if len(partes) > 1:
            tonalidade = partes[1].strip()
            if "maior" in tonalidade:
                tonica = tonalidade.replace("maior", "").strip().upper()
                resultado = theory_teacher.explain_scale(tonica, "major")
            elif "menor" in tonalidade:
                tonica = tonalidade.replace("menor", "").strip().upper()
                resultado = theory_teacher.explain_scale(tonica, "minor")
            else:
                tonica = tonalidade.strip().upper()
                resultado = theory_teacher.explain_scale(tonica, "major")
            
            if "erro" in resultado:
                return {"resposta": resultado["erro"]}
            else:
                resposta = f"Escala de {resultado["escala"]}:\n"
                resposta += f"Notas: {', '.join(resultado['notas'])}\n"
                resposta += f"Padrão: {resultado['padrao']} (T=Tom, S=Semitom)\n"
                resposta += f"Descrição: {resultado['descricao']}"
                return {"resposta": resposta}

    elif "acorde" in texto and ("como formar" in texto or "como fazer" in texto or "formação" in texto):
        # Tenta extrair o acorde específico
        palavras = texto.split()
        for i, palavra in enumerate(palavras):
            if palavra.upper() in theory_teacher.note_names:
                root = palavra.upper()
                # Verifica se há especificação de tipo
                if i + 1 < len(palavras):
                    next_word = palavras[i + 1]
                    if "menor" in next_word or "m" == next_word:
                        chord_type = "minor"
                    elif "maior" in next_word or "M" == next_word:
                        chord_type = "major"
                    elif "7" in next_word:
                        chord_type = "7"
                    else:
                        chord_type = "major"
                else:
                    chord_type = "major"
                
                resultado = theory_teacher.explain_chord(root, chord_type)
                if "erro" in resultado:
                    return {"resposta": resultado["erro"]}
                else:
                    resposta = f"Acorde {resultado["acorde"]}:\n"
                    resposta += f"Notas: {', '.join(resultado['notas'])}\n"
                    resposta += f"Intervalos: {', '.join(resultado['intervalos'])}\n"
                    resposta += f"Descrição: {resultado['descricao']}\n"
                    resposta += f"Progressão sugerida: {resultado['exemplo_progressao']}"
                    return {"resposta": resposta}
                break
        
        return {"resposta": "Para formar acordes básicos: Acorde maior = 1ª + 3ª maior + 5ª justa. Acorde menor = 1ª + 3ª menor + 5ª justa. Especifique um acorde para análise detalhada."}

    elif "intervalo" in texto and ("entre" in texto or "de" in texto):
        # Tenta extrair as duas notas
        palavras = texto.split()
        notas_encontradas = []
        for palavra in palavras:
            if palavra.upper() in theory_teacher.note_names:
                notas_encontradas.append(palavra.upper())
        
        if len(notas_encontradas) >= 2:
            resultado = theory_teacher.explain_interval(notas_encontradas[0], notas_encontradas[1])
            if "erro" in resultado:
                return {"resposta": resultado["erro"]}
            else:
                resposta = f"Intervalo entre {resultado["nota1"]} e {resultado["nota2"]}:\n"
                resposta += f"Intervalo: {resultado['intervalo']} ({resultado['semitons']} semitons)\n"
                resposta += f"Descrição: {resultado['descricao']}\n"
                resposta += f"Exemplo musical: {resultado['exemplo_musical']}"
                return {"resposta": resposta}
        else:
            return {"resposta": "Especifique duas notas para calcular o intervalo. Exemplo: 'intervalo entre C e E'"}

    elif "modo" in texto and any(modo in texto for modo in ["jônio", "dórico", "frígio", "lídio", "mixolídio", "eólio", "lócrio"]):
        # Extrai o modo e a tônica
        palavras = texto.split()
        tonica = None
        modo = None
        
        for palavra in palavras:
            if palavra.upper() in theory_teacher.note_names:
                tonica = palavra.upper()
            for modo_nome in ["jônio", "dórico", "frígio", "lídio", "mixolídio", "eólio", "lócrio"]:
                if modo_nome in palavra.lower():
                    modo = modo_nome
                    break
        
        if tonica and modo:
            resultado = theory_teacher.explain_mode(tonica, modo)
            if "erro" in resultado:
                return {"resposta": resultado["erro"]}
            else:
                resposta = f"Modo {resultado["modo"]}:\n"
                resposta += f"Notas: {', '.join(resultado['notas'])}\n"
                resposta += f"Característica: {resultado['caracteristica']}\n"
                resposta += f"Descrição: {resultado['descricao']}\n"
                resposta += f"Gêneros musicais: {', '.join(resultado['generos_musicais'])}"
                return {"resposta": resposta}
        else:
            return {"resposta": "Especifique a tônica e o modo. Exemplo: 'modo C jônio' ou 'D dórico'"}

    elif "cadência" in texto:
        partes = texto.split("cadência")
        if len(partes) > 1:
            cadence_type = partes[1].strip()
            resultado = theory_teacher.explain_cadence(cadence_type)
            if "erro" in resultado:
                return {"resposta": resultado["erro"]}
            else:
                resposta = f"Cadência {resultado["cadencia"]}:\n"
                resposta += f"Progressão: {resultado['progressao']}\n"
                resposta += f"Descrição: {resultado['descricao']}\n"
                resposta += f"Função: {resultado['funcao']}"
                return {"resposta": resposta}
        else:
            return {"resposta": "Especifique o tipo de cadência. Exemplo: 'cadência autêntica perfeita'"}

    elif "função harmônica" in texto:
        partes = texto.split("função harmônica")
        if len(partes) > 1:
            info = partes[1].strip().split("na tonalidade")
            if len(info) == 2:
                degree = info[0].strip()
                mode = info[1].strip()
                resultado = theory_teacher.explain_harmonic_function(degree, mode)
                if "erro" in resultado:
                    return {"resposta": resultado["erro"]}
                else:
                    resposta = f"Função Harmônica do grau {resultado["grau"]} no modo {resultado["modo"]}:\n"
                    resposta += f"Nome: {resultado['nome']}\n"
                    resposta += f"Descrição: {resultado['descricao']}\n"
                    resposta += f"Exemplos: {', '.join(resultado['exemplos'])}"
                    return {"resposta": resposta}
            else:
                return {"resposta": "Especifique o grau e a tonalidade. Exemplo: 'função harmônica I na tonalidade maior'"}

    elif "exercício" in texto or "exercicio" in texto:
        return {"resposta": "Posso gerar exercícios de teoria musical! Use os botões na interface para gerar exercícios de intervalos, acordes ou escalas. Isso ajudará você a praticar e fixar o conhecimento."}

    else:
        return {"resposta": "Ainda não sei responder essa pergunta, mas estou aprendendo! 🎵 Você pode perguntar sobre escalas, acordes, campo harmônico, intervalos, modos gregos, ou enviar um arquivo de áudio para análise. Também posso gerar exercícios para você praticar!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)