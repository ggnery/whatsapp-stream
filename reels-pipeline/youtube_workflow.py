import os
from pathlib import Path
from youtube_uploader import authenticate_youtube, upload_video, wait_for_video_processing
from csv_manager import get_videos_to_upload, update_youtube_status

# Diretórios
VIDEOS_DIR = "videos"

def processar_video_unico(youtube_service, video_entry, processed_files):
    """
    Processa um único vídeo: faz upload, espera processamento e adiciona resumo ao .md
    
    Args:
        youtube_service: Serviço autenticado do YouTube
        video_entry: Dicionário com informações do vídeo do CSV
        processed_files: Set de arquivos já processados nesta execução
    """
    shortcode = video_entry.get("insta_shortcode", "")
    filename = video_entry.get("filename", "")
    
    if not filename or not shortcode:
        print(f"[YouTubeWorkflow] Erro: Dados incompletos para vídeo {shortcode}")
        return False
    
    # Verifica se este arquivo já foi enviado nesta execução
    if filename in processed_files:
        print(f"[YouTubeWorkflow] Aviso: Arquivo '{filename}' já foi enviado nesta execução. Pulando para evitar duplicata.")
        print(f"[YouTubeWorkflow] Shortcode atual: {shortcode}")
        return False
    
    video_path = Path(VIDEOS_DIR) / filename
    
    if not video_path.exists():
        print(f"[YouTubeWorkflow] Erro: Vídeo não encontrado: {video_path}")
        return False
    
    print("\n" + "="*60)
    print(f"[YouTubeWorkflow] Processando: {filename}")
    print("="*60)
    
    try:
        # Gerar metadados a partir do nome do arquivo
        video_title = video_path.stem.replace("_", " ").replace("-", " ").title()
        video_desc = f"Vídeo processado automaticamente"
        video_tags = ["instagram", "reels", "automacao"]
        
        # === ETAPA 1: UPLOAD ===
        print(f"\n--- Etapa 1: Upload do Vídeo ---")
        video_id = upload_video(
            youtube=youtube_service,
            video_file_path=str(video_path),
            video_title=video_title,
            video_description=video_desc,
            video_tags=video_tags,
            privacy_status="public"  # Vídeos públicos
        )
        
        if not video_id:
            print(f"[YouTubeWorkflow] Falha no upload de {filename}")
            return False
        
        # Atualiza CSV com ID do YouTube (status ainda não é 'uploaded' até processar)
        update_youtube_status(shortcode, video_id, "processing")
        
        # === ETAPA 2: ESPERA DE PROCESSAMENTO ===
        print("\n--- Etapa 2: Aguardando Processamento ---")
        is_processed = wait_for_video_processing(youtube_service, video_id)
        
        if not is_processed:
            print(f"[YouTubeWorkflow] Processamento de {video_id} falhou")
            update_youtube_status(shortcode, video_id, "failed")
            return False
        
        # Atualiza status no CSV com 'uploaded'
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        update_youtube_status(shortcode, video_id, "uploaded")
        
        # Marca arquivo como processado
        processed_files.add(filename)
        
        print(f"\n✅ Vídeo {filename} enviado com sucesso!")
        print(f"   ID do YouTube: {video_id}")
        print(f"   URL: {video_url}")
        
        return True
        
    except Exception as e:
        print(f"[YouTubeWorkflow] Erro crítico ao processar {filename}: {e}")
        return False


def main():
    """
    Função principal que orquestra o upload dos vídeos para o YouTube.
    Processa apenas vídeos que foram baixados mas ainda não enviados.
    """
    print("\n" + "="*60)
    print("[YouTubeWorkflow] Iniciando workflow de Upload para YouTube")
    print("="*60)
    
    try:
        # Busca vídeos que precisam ser enviados
        videos_to_upload = get_videos_to_upload()
        
        if not videos_to_upload:
            print("[YouTubeWorkflow] Nenhum vídeo novo para enviar ao YouTube.")
            print("[YouTubeWorkflow] Processamento concluído!")
            print(f"   Sucesso: 0")
            print(f"   Falhas: 0")
            return
        
        print(f"[YouTubeWorkflow] {len(videos_to_upload)} vídeo(s) encontrado(s) para upload.")
        
        # Autentica no YouTube uma vez
        print("\n[YouTubeWorkflow] Autenticando no YouTube...")
        youtube_service = authenticate_youtube()
        if not youtube_service:
            print("[YouTubeWorkflow] Falha na autenticação. Abortando.")
            return
        
        # Processa cada vídeo
        success_count = 0
        fail_count = 0
        processed_files = set()  # Rastreia arquivos já processados para evitar duplicatas
        
        for video_entry in videos_to_upload:
            if processar_video_unico(youtube_service, video_entry, processed_files):
                success_count += 1
            else:
                fail_count += 1
        
        print("\n" + "="*60)
        print(f"[YouTubeWorkflow] Processamento concluído!")
        print(f"   Sucesso: {success_count}")
        print(f"   Falhas: {fail_count}")
        print("="*60)
        
    except Exception as e:
        print(f"[YouTubeWorkflow] Erro crítico no fluxo principal: {e}")


if __name__ == "__main__":
    main()