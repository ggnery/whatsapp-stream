import os
import time
import google.oauth2.credentials
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# === Constantes do Módulo ===
CLIENT_SECRETS_FILE = "client.json"
TOKEN_FILE = "token.json"

# Escopos necessários: upload e verificação de status
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly" 
]


def authenticate_youtube():
    """
    Autentica o usuário com o YouTube.
    Reutiliza e atualiza o 'token.json' se ele existir.
    Caso contrário, executa o fluxo de login completo.
    """
    credentials = None
    
    if os.path.exists(TOKEN_FILE):
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        print("[Uploader] Token encontrado.")

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("[Uploader] Token expirado. Atualizando...")
            try:
                credentials.refresh(google.auth.transport.requests.Request())
            except Exception as e:
                print(f"[Uploader] Falha ao atualizar token: {e}. Re-autenticando...")
                credentials = None
        
        if not credentials:
            print("[Uploader] Token não encontrado ou inválido. Iniciando fluxo de login...")
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
            
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"Erro: O arquivo '{CLIENT_SECRETS_FILE}' não foi encontrado."
                )
                
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=8080)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())
        print(f"[Uploader] Token salvo em {TOKEN_FILE}")

    print("[Uploader] Autenticação do YouTube concluída.")
    return build("youtube", "v3", credentials=credentials)


def upload_video(youtube, video_file_path, video_title, video_description, video_tags, privacy_status="unlisted", category_id="28"):
    """
    Função de alto nível para fazer o upload.
    Envia o vídeo e retorna o ID do vídeo.
    
    Argumentos:
        youtube (googleapiclient.discovery.Resource): O objeto de serviço da API.
        video_file_path (str): Caminho para o arquivo (ex: "video.mp4")
        video_title (str): Título do vídeo no YouTube.
        video_description (str): Descrição do vídeo.
        video_tags (list): Lista de strings (ex: ["python", "api"])
        privacy_status (str): "public", "private", ou "unlisted"
        category_id (str): "22" (Pessoas e Blogs), "28" (Ciência e Tecnologia)
    """
    try:
        if not os.path.exists(video_file_path):
            print(f"[Uploader] Erro: Arquivo de vídeo não encontrado em '{video_file_path}'")
            return None
        
        request_body = {
            "snippet": {
                "categoryId": category_id,
                "title": video_title,
                "description": video_description,
                "tags": video_tags
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }
        
        media_file = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        )
        
        response = None
        print(f"[Uploader] Iniciando upload de: {video_file_path}")
        
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Progresso do Upload: {int(status.progress() * 100)}%")
        
        video_id = response['id']
        print(f"[Uploader] Upload concluído! ID do Vídeo: {video_id}")
        
        return video_id
        
    except HttpError as e:
        print(f"[Uploader] Erro HTTP durante o upload: {e}")
        return None
    except Exception as e:
        print(f"[Uploader] Erro inesperado durante o upload: {e}")
        return None


def wait_for_video_processing(youtube, video_id, check_interval_seconds=30):
    """
    Verifica o status de processamento de um vídeo.
    Espera até que o vídeo esteja 'succeeded'/'processed' ou 'failed'.
    
    Retorna True se 'succeeded' ou 'processed', False se 'failed'.
    """
    print(f"[Uploader] Aguardando processamento do vídeo (ID: {video_id})...")
    
    while True:
        try:
            # Pede à API o 'status' do vídeo
            request = youtube.videos().list(
                part="status",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                print("[Uploader] Erro: Vídeo não encontrado após o upload.")
                return False
                
            video_status = response['items'][0]['status']
            
            processing_status = video_status.get('processingStatus')
            upload_status = video_status.get('uploadStatus')
            
            print(f"[Uploader] Verificando... (Upload: {upload_status}, Processamento: {processing_status})")
            
            # 1. Condições de Falha
            if processing_status == 'failed':
                print("[Uploader] Processamento do vídeo falhou.")
                return False
                
            if upload_status == 'failed' or upload_status == 'rejected':
                print(f"[Uploader] O upload do vídeo falhou ou foi rejeitado (Status: {upload_status}).")
                return False

            # 2. Condições de Sucesso
            if processing_status == 'succeeded' or upload_status == 'processed':
                print("[Uploader] Processamento do vídeo concluído com sucesso!")
                return True
                
            # 3. Continua esperando
            print(f"[Uploader] Vídeo ainda está em processamento... Nova verificação em {check_interval_seconds}s...")
            time.sleep(check_interval_seconds)
            
        except HttpError as e:
            print(f"[Uploader] Erro HTTP ao verificar status: {e}")
            time.sleep(check_interval_seconds)
        except Exception as e:
            print(f"[Uploader] Erro inesperado ao verificar status: {e}")
            return False