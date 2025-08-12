from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
import logging
from typing import Dict, Any, Optional

from audio_analysis import AudioAnalyzer
from music_theory import MusicTheoryTeacher, generate_exercise
from chat_processor import ChatProcessor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do FastAPI
app = FastAPI(
    title="🎼 Agente Musical de IA",
    description="API para análise de áudio e ensino de teoria musical",
    version="2.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicialização dos componentes
audio_analyzer = AudioAnalyzer()
theory_teacher = MusicTheoryTeacher()
chat_processor = ChatProcessor(theory_teacher)

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str

class ExerciseRequest(BaseModel):
    type: str

class AnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Rota principal
@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve a página principal da aplicação."""
    try:
        # Carrega o HTML do frontend 
        html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎼 Agente Musical de IA</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding: 40px 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }

        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
        }

        .audio-upload {
            border: 2px dashed #667eea;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            background: linear-gradient(45deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            margin-bottom: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            width: 100%;
            margin-top: 15px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }

        .chat-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .chat-messages {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            background: rgba(248, 249, 250, 0.8);
        }

        .message {
            margin-bottom: 15px;
            padding: 15px 20px;
            border-radius: 15px;
            max-width: 80%;
            animation: fadeInUp 0.3s ease;
        }

        .user-message {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            margin-left: auto;
            text-align: right;
        }

        .bot-message {
            background: linear-gradient(45deg, #4ecdc4, #44a08d);
            color: white;
            margin-right: auto;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎼 Agente Musical de IA</h1>
            <p>Análise de áudio, ensino de teoria musical e exercícios interativos</p>
        </div>

        <div class="main-grid">
            <div class="card">
                <h2>🎵 Análise de Áudio</h2>
                <div class="audio-upload" onclick="document.getElementById('audioFile').click()">
                    <span style="font-size: 3rem; color: #667eea; display: block; margin-bottom: 15px;">🎧</span>
                    <div>Clique para selecionar seu arquivo de áudio</div>
                    <div style="font-size: 0.9rem; color: #999; margin-top: 10px;">Suporta WAV, MP3, FLAC, M4A</div>
                    <input type="file" id="audioFile" accept="audio/*" style="display: none;">
                </div>
                <button class="btn" id="analyzeBtn" disabled onclick="analyzeAudio()">Analisar Áudio</button>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <div>Analisando áudio...</div>
                </div>
                <div id="results"></div>
            </div>

            <div class="card">
                <h2>🎯 Exercícios Musicais</h2>
                <p style="margin-bottom: 20px;">Pratique teoria musical:</p>
                <button class="btn" onclick="generateExercise('interval')" style="margin: 5px; width: auto; padding: 10px 20px;">Intervalos</button>
                <button class="btn" onclick="generateExercise('chord')" style="margin: 5px; width: auto; padding: 10px 20px;">Acordes</button>
                <button class="btn" onclick="generateExercise('scale')" style="margin: 5px; width: auto; padding: 10px 20px;">Escalas</button>
                <div id="exercise-results"></div>
            </div>
        </div>

        <div class="chat-container">
            <h2>🤖 Chat de Teoria Musical</h2>
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    Olá! 👋 Sou seu assistente musical de IA. Posso responder perguntas sobre teoria musical!
                    <br><br>
                    <strong>Experimente perguntar:</strong><br>
                    • "escala de D maior"<br>
                    • "campo harmônico de A menor"<br>
                    • "acorde G7"<br>
                    • "intervalo entre F e A"
                </div>
            </div>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="chatInput" placeholder="Digite sua pergunta sobre teoria musical..." 
                       style="flex: 1; padding: 15px 20px; border: 1px solid #ddd; border-radius: 50px; font-size: 1rem; outline: none;"
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button class="btn" onclick="sendMessage()" style="width: auto; margin: 0; padding: 15px 30px;">Enviar</button>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = '';

        document.getElementById('audioFile').addEventListener('change', function() {
            const btn = document.getElementById('analyzeBtn');
            btn.disabled = !this.files.length;
        });

        async function analyzeAudio() {
            const fileInput = document.getElementById('audioFile');
            const file = fileInput.files[0];
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            if (!file) return;
            
            loading.style.display = 'block';
            results.innerHTML = '';
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/api/analyze-audio', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data.analysis);
                } else {
                    results.innerHTML = `<div style="color: red; padding: 15px;">Erro: ${data.error}</div>`;
                }
            } catch (error) {
                results.innerHTML = `<div style="color: red; padding: 15px;">Erro na análise: ${error.message}</div>`;
            } finally {
                loading.style.display = 'none';
            }
        }

        function displayResults(analysis) {
            const results = document.getElementById('results');
            results.innerHTML = `
                <div style="background: white; padding: 20px; border-radius: 15px; margin-top: 15px;">
                    <h3>📊 Resultados da Análise</h3>
                    <p><strong>🎵 Tonalidade:</strong> ${analysis.tonalidade}</p>
                    <p><strong>⏱️ Tempo:</strong> ${analysis.tempo} BPM</p>
                    <p><strong>⏰ Duração:</strong> ${Math.floor(analysis.duracao / 60)}:${String(Math.floor(analysis.duracao % 60)).padStart(2, '0')}</p>
                    <p><strong>🎸 Acordes:</strong> ${analysis.acordes_detectados.join(', ')}</p>
                    ${analysis.progressao_sugerida ? `<p><strong>🎼 Campo Harmônico:</strong> ${analysis.progressao_sugerida.join(', ')}</p>` : ''}
                </div>
            `;
        }

        async function generateExercise(type) {
            const results = document.getElementById('exercise-results');
            
            try {
                const response = await fetch('/api/generate-exercise', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ type })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayExercise(data.exercise);
                } else {
                    results.innerHTML = `<div style="color: red;">Erro: ${data.error}</div>`;
                }
            } catch (error) {
                results.innerHTML = `<div style="color: red;">Erro: ${error.message}</div>`;
            }
        }

        function displayExercise(exercise) {
            const results = document.getElementById('exercise-results');
            results.innerHTML = `
                <div style="background: white; padding: 20px; border-radius: 15px; margin-top: 15px;">
                    <h4>${exercise.tipo}</h4>
                    <p style="font-size: 1.2rem; margin: 15px 0;"><strong>${exercise.pergunta}</strong></p>
                    <button onclick="showAnswer(this)" style="background: #ff6b6b; color: white; border: none; padding: 10px 20px; border-radius: 25px; cursor: pointer;">Mostrar Resposta</button>
                    <div style="display: none; margin-top: 15px; padding: 15px; background: #f0f8f0; border-radius: 10px;">
                        ${formatAnswer(exercise.resposta)}
                    </div>
                </div>
            `;
        }

        function formatAnswer(answer) {
            if (answer.erro) return answer.erro;
            
            let html = '';
            if (answer.notas) html += `<p><strong>Notas:</strong> ${answer.notas.join(' - ')}</p>`;
            if (answer.intervalos) html += `<p><strong>Intervalos:</strong> ${answer.intervalos.join(', ')}</p>`;
            if (answer.intervalo) html += `<p><strong>Intervalo:</strong> ${answer.intervalo} (${answer.semitons} semitons)</p>`;
            if (answer.descricao) html += `<p><strong>Descrição:</strong> ${answer.descricao}</p>`;
            
            return html || '<p>Resposta não disponível.</p>';
        }

        function showAnswer(button) {
            const answer = button.nextElementSibling;
            if (answer.style.display === 'none') {
                answer.style.display = 'block';
                button.textContent = 'Ocultar Resposta';
            } else {
                answer.style.display = 'none';
                button.textContent = 'Mostrar Resposta';
            }
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            input.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();
                addMessage(data.response, 'bot');
            } catch (error) {
                addMessage('Erro ao processar mensagem: ' + error.message, 'bot');
            }
        }

        function addMessage(text, sender) {
            const messages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = text;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Erro ao servir página principal: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# API Endpoints

@app.post("/api/analyze-audio", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """Analisa um arquivo de áudio e retorna informações musicais."""
    
    # Validação do arquivo
    if not file.content_type or not file.content_type.startswith('audio/'):
        return AnalysisResponse(
            success=False, 
            error="Formato de arquivo não suportado. Use arquivos de áudio (WAV, MP3, FLAC, etc.)"
        )
    
    # Limite de tamanho (10MB)
    max_size = 10 * 1024 * 1024  # 10MB em bytes
    
    try:
        # Salva arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            
            if len(content) > max_size:
                return AnalysisResponse(
                    success=False,
                    error="Arquivo muito grande. Máximo permitido: 10MB"
                )
            
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"Analisando arquivo: {file.filename} ({len(content)} bytes)")
        
        # Analisa o áudio
        analysis_result = audio_analyzer.analyze_audio_file(temp_file_path)
        
        # Remove arquivo temporário
        os.unlink(temp_file_path)
        
        # Verifica se houve erro na análise
        if "erro" in analysis_result:
            return AnalysisResponse(
                success=False,
                error=analysis_result["erro"]
            )
        
        # Adiciona campo harmônico se a tonalidade foi detectada
        if "tonalidade" in analysis_result:
            try:
                # Extrai tonalidade e modo
                tonalidade = analysis_result["tonalidade"]
                if "maior" in tonalidade.lower():
                    tonica = tonalidade.replace("maior", "").strip()
                    campo_harmonico = theory_teacher.explain_harmonic_field(tonica, "major")
                elif "menor" in tonalidade.lower():
                    tonica = tonalidade.replace("menor", "").strip()
                    campo_harmonico = theory_teacher.explain_harmonic_field(tonica, "minor")
                else:
                    campo_harmonico = None
                
                if campo_harmonico and "erro" not in campo_harmonico:
                    analysis_result["progressao_sugerida"] = [
                        acorde["cifra"] for acorde in campo_harmonico["acordes"]
                    ]
            except Exception as e:
                logger.warning(f"Erro ao gerar campo harmônico: {str(e)}")
        
        logger.info(f"Análise concluída com sucesso para: {file.filename}")
        
        return AnalysisResponse(success=True, analysis=analysis_result)
        
    except Exception as e:
        
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
        
        logger.error(f"Erro na análise de áudio: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=f"Erro durante a análise: {str(e)}"
        )

@app.post("/api/generate-exercise")
async def generate_exercise_endpoint(request: ExerciseRequest):
    """Gera um exercício de teoria musical."""
    try:
        logger.info(f"Gerando exercício do tipo: {request.type}")
        
        exercise = generate_exercise(request.type)
        
        if "erro" in exercise:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": exercise["erro"]}
            )
        
        return {"success": True, "exercise": exercise}
        
    except Exception as e:
        logger.error(f"Erro ao gerar exercício: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Erro interno: {str(e)}"}
        )

@app.post("/api/chat")
async def chat_endpoint(message: ChatMessage):
    """Processa mensagens do chat de teoria musical."""
    try:
        logger.info(f"Processando mensagem do chat: {message.message[:50]}...")
        
        response = chat_processor.process_message(message.message)
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Erro no chat: {str(e)}")
        return {"response": f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"}

# Endpoints de informação
@app.get("/api/health")
async def health_check():
    """Verifica o status da API."""
    return {
        "status": "healthy",
        "message": "Agente Musical de IA está funcionando!",
        "components": {
            "audio_analyzer": "OK",
            "theory_teacher": "OK",
            "chat_processor": "OK"
        }
    }

@app.get("/api/info")
async def get_api_info():
    """Retorna informações sobre a API."""
    return {
        "name": "🎼 Agente Musical de IA",
        "version": "2.0.0",
        "description": "API para análise de áudio e ensino de teoria musical",
        "features": [
            "Análise de áudio (tonalidade, tempo, acordes)",
            "Ensino de teoria musical",
            "Exercícios interativos",
            "Chat inteligente",
            "Campo harmônico",
            "Intervalos e escalas"
        ],
        "supported_audio_formats": ["WAV", "MP3", "FLAC", "M4A", "OGG"],
        "max_file_size": "10MB"
    }

# Tratamento de erros
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Tratamento geral de exceções."""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🎼 Iniciando Agente Musical de IA...")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True  # Para desenvolvimento
    )