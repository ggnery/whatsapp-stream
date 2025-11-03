import instaloader
from urllib.parse import urlparse
from pathlib import Path
import glob
import os
import sys # Importar sys para sair do script em caso de erro

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

def shortcodes_from_txt(txt_path: str):
    """Lê o TXT e retorna shortcodes únicos (deduplicados)."""
    codes = set()
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            sc = extract_shortcode(line)
            if sc:
                codes.add(sc)
    return sorted(codes)

def unique_path(base_path: Path) -> Path:
    """Gera nome único se já existir (ex.: dd-mm-yyyy.mp4 -> dd-mm-yyyy_2.mp4)."""
    if not base_path.exists():
        return base_path
    stem, suf = base_path.stem, base_path.suffix
    i = 2
    while True:
        candidate = base_path.with_name(f"{stem}_{i}{suf}")
        if not candidate.exists():
            return candidate
        i += 1

def main():
    # Define os diretórios de forma relativa
    links_dir = "link-reels"
    out_dir = "videos"

    # Procura pelo arquivo .txt na pasta de links
    txt_files = glob.glob(os.path.join(links_dir, "*.txt"))
    if len(txt_files) == 0:
        print(f"❌ Erro: Nenhum arquivo .txt encontrado na pasta '{links_dir}'.")
        sys.exit(1)
    elif len(txt_files) > 1:
        print(f"⚠️ Aviso: Múltiplos arquivos .txt encontrados em '{links_dir}'. Usando o primeiro: {os.path.basename(txt_files[0])}")
    txt_path = txt_files[0]


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

    shortcodes = shortcodes_from_txt(txt_path)
    print(f"Encontrados {len(shortcodes)} shortcodes únicos para download.")

    ok = 0
    fail = 0
    skip = 0 # Contador para vídeos pulados
    for sc in shortcodes:
        try:
            post = instaloader.Post.from_shortcode(loader.context, sc)

            # Se não for vídeo, pula (como Reels é vídeo, mas fica a checagem)
            if not post.is_video:
                print(f"[INFO] {sc} não é vídeo — ignorando.")
                continue

            # --- LÓGICA PARA PULAR VÍDEOS JÁ EXISTENTES ---
            # Pega a data e verifica se um arquivo com esse padrão de nome já existe
            date_str = post.date_local.strftime("%d-%m-%Y")
            # Procura por 'dd-mm-yyyy.mp4' ou 'dd-mm-yyyy_*.mp4'
            existing_files = list(glob.glob(os.path.join(out_dir, f"{date_str}*.mp4")))
            if existing_files:
                print(f"[PULANDO] Vídeo para {sc} (data: {date_str}) já existe: {Path(existing_files[0]).name}")
                skip += 1
                continue
            # --- FIM DA LÓGICA ---

            # Baixa o post (gera <shortcode>.mp4 e às vezes .txt; depois limpamos/renomeamos)
            loader.download_post(post, target=out_dir)

            # Caminhos candidatos (em caso de carrossel com múltiplos vídeos, viria *_1, *_2, etc.)
            mp4_candidates = sorted(glob.glob(os.path.join(out_dir, f"{sc}*.mp4")))
            if not mp4_candidates:
                print(f"[AVISO] {sc} baixado mas .mp4 não encontrado.")
                continue

            # Data de publicação (local) no formato dd-mm-yyyy
            date_str = post.date_local.strftime("%d-%m-%Y")

            # Renomeia cada .mp4 encontrado
            for idx, old in enumerate(mp4_candidates, start=1):
                old_p = Path(old)
                # Se houver mais de um vídeo (carrossel), acrescenta sufixo _2, _3...
                base_name = date_str if len(mp4_candidates) == 1 else f"{date_str}_{idx}"
                new_p = unique_path(Path(out_dir) / f"{base_name}.mp4")
                old_p.replace(new_p)
                print(f"OK: {sc} → {new_p.name}")

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