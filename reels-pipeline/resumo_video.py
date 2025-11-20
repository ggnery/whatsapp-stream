from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import time

# Carrega as variáveis de ambiente
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def obter_resumo_do_video(video_url: str):
    """
    Recebe uma URL de vídeo do YouTube e retorna o resumo
    usando a API Gemini (método Client).
    Inclui lógica de retry para erros 503 (API sobrecarregada).
    """
    
    print(f"[ResumoVideo] Inicializando cliente para resumir a URL: {video_url}")
    
    if not GEMINI_API_KEY:
        print("[ResumoVideo] Erro: GEMINI_API_KEY não encontrada no .env.")
        return None

    model = "models/gemini-2.5-pro"
    prompt = """"Forneça um resumo geral conciso do vídeo. Logo em seguida, liste os tópicos principais e seus respectivos timestamps do vídeo.

            Formate cada tópico como:
            - **[Nome do Tópico]** ([HH:MM:SS]) - [Breve descrição do tópico]

            Certifique-se de que os tempos de gravação estejam no formato exato [HH:MM:SS]. Não inclua nenhum texto conversacional ou introduções adicionais."
            """
    
    # Lógica de Novas Tentativas (Retries)
    max_retries = 3
    initial_wait_seconds = 5
    
    try:
        # Inicializa o cliente
        client = genai.Client(api_key=GEMINI_API_KEY)

        for attempt in range(max_retries):
            try:
                print(f"[ResumoVideo] Enviando requisição para a API Gemini (Tentativa {attempt + 1}/{max_retries})...")
                response = client.models.generate_content(
                    model=model,
                    contents=types.Content(
                        parts = [
                            types.Part(file_data=types.FileData(file_uri=video_url)),
                            types.Part(text=prompt)
                        ]
                    )
                )

                result = response.candidates[0].content.parts[0].text
                print("[ResumoVideo] Resumo recebido com sucesso.")
                return result
                
            except Exception as e:
                # Verifica se o erro é o 503 (sobrecarregado)
                error_message = str(e)
                if "503" in error_message or "UNAVAILABLE" in error_message or "overloaded" in error_message:
                    
                    if attempt + 1 == max_retries:
                        print(f"[ResumoVideo] API sobrecarregada. Falha após {max_retries} tentativas.")
                        break
                    
                    # Calcula o tempo de espera (espera exponencial)
                    wait_time = initial_wait_seconds * (2 ** attempt) 
                    print(f"[ResumoVideo] API sobrecarregada (Erro 503). Tentando novamente em {wait_time}s...")
                    time.sleep(wait_time)
                
                else:
                    # Se for qualquer outro erro
                    print(f"[ResumoVideo] Ocorreu um erro não recuperável: {e}")
                    return None
            
        # Se o loop terminar sem sucesso
        print("[ResumoVideo] Não foi possível obter o resumo após todas as tentativas.")
        return None

    except Exception as e:
        # Este 'except' captura erros na inicialização do cliente
        print(f"[ResumoVideo] Ocorreu um erro crítico ao inicializar o cliente: {e}")
        return None


if __name__ == "__main__":
    print("Executando resumo_video.py como script de teste...")
    
    url_de_teste = "https://www.youtube.com/watch?v=pQtqcDbYmK4" 
    
    resumo = obter_resumo_do_video(url_de_teste)
    
    if resumo:
        print("\n--- RESULTADO DO TESTE ---")
        print(resumo)
        print("--- FIM DO TESTE ---")
    else:
        print("Teste falhou. Não foi possível obter o resumo.")