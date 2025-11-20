"""
Gerador de resumos de vídeos do YouTube usando Gemini.
Processa vídeos que foram enviados ao YouTube mas ainda não têm resumo.
RESPONSABILIDADE: Gerar resumo do vídeo do YouTube e adicionar ao arquivo .md
"""
from pathlib import Path
from resumo_video import obter_resumo_do_video
from csv_manager import load_registry


# Diretórios
TRANSCRIPTIONS_DIR = "transcriptions"


def processar_resumo_video(video_entry):
    """
    Gera resumo de um vídeo do YouTube e adiciona ao arquivo .md
    
    Args:
        video_entry: Dicionário com informações do vídeo do CSV
    
    Returns:
        True se sucesso, False se falha
    """
    shortcode = video_entry.get("insta_shortcode", "")
    youtube_id = video_entry.get("youtube_id", "")
    filename = video_entry.get("filename", "")
    
    # Nome do .md é o mesmo que o filename sem extensão
    if filename:
        md_name = filename.replace(".mp4", "")
    else:
        md_name = ""
    
    if not youtube_id or not shortcode or not md_name:
        print(f"[GeminiSummary] Erro: Dados incompletos para vídeo {shortcode}")
        return False
    
    video_url = f"https://www.youtube.com/watch?v={youtube_id}"
    
    print("\n" + "="*60)
    print(f"[GeminiSummary] Processando: {md_name}.md")
    print(f"[GeminiSummary] URL: {video_url}")
    print("="*60)
    
    try:
        # Verifica se o arquivo .md existe
        md_filename = f"{md_name}.md"
        md_path = Path(TRANSCRIPTIONS_DIR) / md_filename
        
        if not md_path.exists():
            print(f"[GeminiSummary] Aviso: Arquivo .md não encontrado: {md_path}")
            print(f"[GeminiSummary] Pulando este vídeo.")
            return False
        
        # Verifica se já tem resumo do YouTube
        with open(md_path, "r", encoding="utf-8") as f:
            conteudo_existente = f.read()
        
        if "## Resumo do Vídeo (YouTube - Gemini)" in conteudo_existente:
            print(f"[GeminiSummary] Resumo já existe em {md_filename}. Pulando.")
            return True  # Já processado, não é erro
        
        # Solicita resumo ao Gemini
        print(f"\n--- Gerando Resumo com Gemini ---")
        print(f"[GeminiSummary] Solicitando resumo para: {video_url}")
        resumo = obter_resumo_do_video(video_url)
        
        if not resumo:
            print("[GeminiSummary] Não foi possível obter o resumo.")
            return False
        
        # Adiciona o resumo do Gemini no final do arquivo
        resumo_section = f"""\n\n## Resumo do Vídeo (YouTube - Gemini)

**URL do Vídeo:** {video_url}
**ID do Vídeo:** {youtube_id}

{resumo}
"""
        
        # Salva com o resumo adicionado
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(conteudo_existente + resumo_section)
        
        print(f"\n✅ Resumo adicionado com sucesso ao {md_filename}")
        return True
        
    except Exception as e:
        print(f"[GeminiSummary] Erro crítico ao processar {shortcode}: {e}")
        return False


def main():
    """
    Função principal que processa resumos de vídeos do YouTube.
    Processa apenas vídeos que foram enviados ao YouTube (status='uploaded')
    """
    print("\n" + "="*60)
    print("[GeminiSummary] Iniciando geração de resumos do YouTube")
    print("="*60)
    
    try:
        # Carrega o registro do CSV
        registry = load_registry()
        
        # Filtra vídeos que foram enviados ao YouTube mas ainda não têm resumo
        videos_to_process = []
        
        for shortcode, entry in registry.items():
            youtube_status = entry.get("youtube_status", "")
            youtube_id = entry.get("youtube_id", "")
            filename = entry.get("filename", "")
            
            if youtube_status == "uploaded" and youtube_id and filename:
                # Verifica se já tem resumo do YouTube no .md
                md_name = filename.replace(".mp4", "")
                md_path = Path(TRANSCRIPTIONS_DIR) / f"{md_name}.md"
                
                if md_path.exists():
                    with open(md_path, "r", encoding="utf-8") as f:
                        conteudo = f.read()
                    
                    # Se já tem resumo, pula
                    if "## Resumo do Vídeo (YouTube - Gemini)" in conteudo:
                        continue
                
                videos_to_process.append(entry)
        
        if not videos_to_process:
            print("[GeminiSummary] Nenhum vídeo novo para processar.")
            print("[GeminiSummary] Processamento concluído!")
            print(f"   Sucesso: 0")
            print(f"   Falhas: 0")
            return
        
        print(f"[GeminiSummary] {len(videos_to_process)} vídeo(s) encontrado(s) para processar.")
        
        # Processa cada vídeo
        success_count = 0
        fail_count = 0
        
        for video_entry in videos_to_process:
            if processar_resumo_video(video_entry):
                success_count += 1
            else:
                fail_count += 1
        
        print("\n" + "="*60)
        print(f"[GeminiSummary] Processamento concluído!")
        print(f"   Sucesso: {success_count}")
        print(f"   Falhas: {fail_count}")
        print("="*60)
        
    except Exception as e:
        print(f"[GeminiSummary] Erro crítico no fluxo principal: {e}")


if __name__ == "__main__":
    main()

