import instaloader
from urllib.parse import urlparse
from pathlib import Path
import glob
import os
import sys 
from csv_manager import (
    is_downloaded, register_download, get_next_number_for_date,
    get_links_from_registry, get_final_filename
)

def extract_shortcode(url: str):
    """Extrai o shortcode de URLs /reel/<code>/, /p/<code>/ ou /tv/<code>/."""
    try:
        path = urlparse(url.strip()).path.strip("/")
        parts = [p for p in path.split("/") if p]
        for i, p in enumerate(parts):
            if p in ("reel", "p", "tv") and i + 1 < len(parts):
                sc = parts[i + 1].split("?")[0].split("#")[0]
                return sc
        if parts:
            sc = parts[-1].split("?")[0].split("#")[0]
            return sc or None
    except Exception:
        pass
    return None

def shortcodes_from_csv():
    """
    Lê o CSV e retorna shortcodes únicos que precisam ser processados.
    Retorna apenas links com status "discovered" (não "downloaded").
    Retorna também um dicionário mapeando shortcode -> link original.
    """
    from csv_manager import load_registry
    registry = load_registry()
    shortcodes = []
    shortcode_to_link = {}
    
    for sc, entry in registry.items():
        link = entry.get("insta_link", "")
        download_status = entry.get("download_status", "")
        
        # Só inclui se tiver link E download_status for "discovered" (não "downloaded")
        if link and download_status == "discovered":
            shortcodes.append(sc)
            shortcode_to_link[sc] = link
    
    return sorted(shortcodes), shortcode_to_link

def get_unique_filename_for_date(date_str: str, out_dir: Path) -> Path:
    """
    Gera nome único para uma data, considerando múltiplos vídeos com mesma data.
    Formato: dd-mm-yyyy-N.mp4 onde N é o próximo número disponível.
    """
    # Verifica quantos vídeos já existem com essa data
    next_num = get_next_number_for_date(date_str, out_dir)
    
    if next_num == 1:
        # Primeiro vídeo com essa data: usa apenas a data
        base_name = f"{date_str}.mp4"
    else:
        # Múltiplos vídeos: adiciona número
        base_name = f"{date_str}-{next_num}.mp4"
    
    return out_dir / base_name

def main():
    # Define os diretórios de forma relativa
    out_dir = "videos"

    # Lê shortcodes do CSV
    try:
        shortcodes, shortcode_to_link = shortcodes_from_csv()
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        sys.exit(1)
    
    if len(shortcodes) == 0:
        print(f"Nenhum vídeo novo para baixar. Todos os vídeos já foram processados.")
        print(f"Concluído: 0 baixados, 0 falharam, 0 pulados. Vídeos em: {Path(out_dir).resolve()}")
        return  # Sai sem erro para continuar o pipeline

    # Instaloader configurado para baixar SOMENTE o vídeo .mp4
    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern=None,   
        dirname_pattern=out_dir,          
        filename_pattern="{shortcode}"    # baixamos como <shortcode>.mp4 e renomeamos depois
    )

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    print(f"Encontrados {len(shortcodes)} shortcodes únicos para download.")

    ok = 0
    fail = 0
    skip = 0 # Contador para vídeos pulados
    
    # Rastreia nomes de arquivos usados nesta execução para evitar sobrescrita
    used_filenames_this_run = set()
    
    for sc in shortcodes:
        try:
            # --- VERIFICAÇÃO ANTES DE BAIXAR (usando CSV) ---
            if is_downloaded(sc):
                final_name = get_final_filename(sc)
                print(f"[PULANDO] {sc} já foi baixado: {final_name}")
                skip += 1
                continue
            # --- FIM DA VERIFICAÇÃO ---
            
            post = instaloader.Post.from_shortcode(loader.context, sc)

            # Se não for vídeo, pula (como Reels é vídeo, mas fica a checagem)
            if not post.is_video:
                print(f"[INFO] {sc} não é vídeo — ignorando.")
                continue

            # Baixa o post (gera <shortcode>.mp4 e às vezes .txt; depois limpamos/renomeamos)
            loader.download_post(post, target=out_dir)

            # Caminhos candidatos (em caso de carrossel com múltiplos vídeos, viria *_1, *_2, etc.)
            mp4_candidates = sorted(glob.glob(os.path.join(out_dir, f"{sc}*.mp4")))
            if not mp4_candidates:
                print(f"[AVISO] {sc} baixado mas .mp4 não encontrado.")
                continue

            # Data de publicação (local) no formato dd-mm-yyyy
            date_str = post.date_local.strftime("%d-%m-%Y")
            
            # Link original do post
            link = shortcode_to_link.get(sc, f"https://www.instagram.com/reel/{sc}/")

            # Renomeia cada .mp4 encontrado
            # Para carrosséis, precisa calcular o número base uma única vez
            base_num = get_next_number_for_date(date_str, Path(out_dir))
            
            for idx, old in enumerate(mp4_candidates, start=1):
                old_p = Path(old)
                original_filename = old_p.name
                
                # Para múltiplos vídeos do mesmo post (carrossel), usa numeração sequencial
                if len(mp4_candidates) > 1:
                    # Carrossel: usa base_num + (idx - 1) para sequência contínua
                    final_name = f"{date_str}-{base_num + idx - 1}.mp4"
                else:
                    # Vídeo único: usa apenas a data se for o primeiro, senão adiciona número
                    if base_num == 1:
                        final_name = f"{date_str}.mp4"
                    else:
                        final_name = f"{date_str}-{base_num}.mp4"
                
                # Verifica se o nome já foi usado nesta execução e ajusta se necessário
                counter = 2
                base_name_without_ext = final_name.replace(".mp4", "")
                while final_name in used_filenames_this_run or (Path(out_dir) / final_name).exists():
                    # Se o nome base já tem número (ex: dd-mm-yyyy-1), remove
                    if base_name_without_ext.count("-") > 2:
                        # Tem formato dd-mm-yyyy-N, pega só a data
                        parts = base_name_without_ext.split("-")
                        base_date = "-".join(parts[:3])  # dd-mm-yyyy
                        final_name = f"{base_date}-{counter}.mp4"
                    else:
                        # Formato simples dd-mm-yyyy
                        final_name = f"{base_name_without_ext}-{counter}.mp4"
                    
                    print(f"[INFO] Nome em conflito. Tentando: {final_name}")
                    counter += 1
                    
                    # Proteção contra loop infinito
                    if counter > 100:
                        print(f"[ERRO] Não foi possível encontrar nome único após 100 tentativas")
                        break
                
                # Registra nome usado
                used_filenames_this_run.add(final_name)
                
                new_p = Path(out_dir) / final_name
                old_p.replace(new_p)
                
                # Registra no CSV
                register_download(
                    link=link,
                    shortcode=sc,
                    filename=final_name,
                    download_status="downloaded"
                )
                
                print(f"OK: {sc} → {final_name}")

            # Remove lixo (.txt/.json etc) que porventura tenha sido criado
            for ext in ("txt", "json", "json.xz", "xz"):
                for junk in glob.glob(os.path.join(out_dir, f"{sc}*.{ext}")):
                    try:
                        os.remove(junk)
                    except Exception:
                        pass

            ok += 1

        except Exception as e:
            print(f"[ERRO] {sc}: {e}")
            fail += 1

    print(f"Concluído: {ok} baixados, {fail} falharam, {skip} pulados. Vídeos em: {Path(out_dir).resolve()}")

if __name__ == "__main__":
    main()