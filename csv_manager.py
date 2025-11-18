import csv
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple

CSV_DIR = "info-reels"
CSV_FILE = "registry.csv"
CSV_COLUMNS = ["insta_link", "insta_shortcode", "filename", "download_status", "youtube_id", "youtube_status"]

def get_csv_path() -> Path:
    """Retorna o caminho completo do arquivo CSV."""
    csv_dir = Path(__file__).parent / CSV_DIR
    csv_dir.mkdir(parents=True, exist_ok=True)
    return csv_dir / CSV_FILE

def load_registry() -> Dict[str, Dict[str, str]]:
    """
    Carrega o registro de downloads do CSV.
    Retorna um dicionário: {insta_shortcode: {coluna: valor}}
    """
    csv_path = get_csv_path()
    registry = {}
    
    if not csv_path.exists():
        return registry
    
    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sc = row.get("insta_shortcode", "")
                if sc:
                    registry[sc] = row
    except Exception as e:
        print(f"⚠️ Erro ao ler CSV: {e}")
    
    return registry

def save_registry(registry: Dict[str, Dict[str, str]]):
    """Salva o registro no CSV."""
    csv_path = get_csv_path()
    
    # Garante que o diretório existe
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Converte dicionário para lista de linhas
    rows = list(registry.values())
    
    # Ordena por insta_shortcode para consistência
    rows.sort(key=lambda x: x.get("insta_shortcode", ""))
    
    try:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"⚠️ Erro ao salvar CSV: {e}")

def is_downloaded(shortcode: str) -> bool:
    """Verifica se um shortcode já foi baixado (download_status = 'downloaded')."""
    registry = load_registry()
    entry = registry.get(shortcode, {})
    return entry.get("download_status") == "downloaded"

def get_final_filename(shortcode: str) -> Optional[str]:
    """Retorna o nome do arquivo se já foi baixado."""
    registry = load_registry()
    entry = registry.get(shortcode, {})
    return entry.get("filename")

def register_download(link: str, shortcode: str, filename: str, 
                     download_status: str = "downloaded"):
    """Registra um download no CSV."""
    registry = load_registry()
    
    # Mantém dados de YouTube se já existirem
    existing_youtube_id = ""
    existing_youtube_status = ""
    if shortcode in registry:
        existing_youtube_id = registry[shortcode].get("youtube_id", "")
        existing_youtube_status = registry[shortcode].get("youtube_status", "")
    
    registry[shortcode] = {
        "insta_link": link,
        "insta_shortcode": shortcode,
        "filename": filename,
        "download_status": download_status,
        "youtube_id": existing_youtube_id,
        "youtube_status": existing_youtube_status
    }
    save_registry(registry)

def get_next_number_for_date(date_str: str, out_dir: Path) -> int:
    """
    Retorna o próximo número disponível para uma data específica.
    Procura por arquivos no formato: date-1.mp4, date-2.mp4, etc.
    """
    pattern = f"{date_str}-*.mp4"
    existing = list(out_dir.glob(pattern))
    
    if not existing:
        return 1
    
    # Extrai números dos arquivos existentes
    numbers = []
    for file in existing:
        stem = file.stem  # ex: "02-08-2024-1"
        parts = stem.split("-")
        if len(parts) >= 4:  # dd-mm-yyyy-N
            try:
                num = int(parts[-1])
                numbers.append(num)
            except ValueError:
                pass
    
    return max(numbers, default=0) + 1

def get_links_from_registry() -> List[str]:
    """Retorna lista de todos os links já registrados."""
    registry = load_registry()
    return [entry.get("insta_link", "") for entry in registry.values() if entry.get("insta_link")]

def register_link(link: str, shortcode: str):
    """
    Registra um novo link no CSV (durante scraping).
    Se o shortcode já existir, atualiza o link se necessário.
    """
    registry = load_registry()
    
    # Se já existe, mantém os dados existentes mas atualiza o link se necessário
    if shortcode in registry:
        if not registry[shortcode].get("insta_link") or registry[shortcode].get("insta_link") != link:
            registry[shortcode]["insta_link"] = link
    else:
        # Novo registro: apenas link e shortcode, outras colunas vazias
        registry[shortcode] = {
            "insta_link": link,
            "insta_shortcode": shortcode,
            "filename": "",
            "download_status": "discovered",  # Status inicial: apenas descoberto, não baixado
            "youtube_id": "",
            "youtube_status": ""
        }
    
    save_registry(registry)

def update_youtube_status(shortcode: str, youtube_id: str, youtube_status: str = "uploaded"):
    """
    Atualiza o status de upload no YouTube para um shortcode.
    """
    registry = load_registry()
    if shortcode in registry:
        registry[shortcode]["youtube_id"] = youtube_id
        registry[shortcode]["youtube_status"] = youtube_status
        save_registry(registry)

def get_videos_to_upload() -> List[Dict[str, str]]:
    """
    Retorna lista de vídeos que precisam ser enviados ao YouTube.
    Critério: download_status='downloaded' E youtube_status vazio ou != 'uploaded'
    """
    registry = load_registry()
    videos_to_upload = []
    
    for shortcode, entry in registry.items():
        download_status = entry.get("download_status", "")
        youtube_status = entry.get("youtube_status", "")
        filename = entry.get("filename", "")
        
        # Só processa vídeos baixados que ainda não foram enviados ao YouTube
        if download_status == "downloaded" and youtube_status != "uploaded" and filename:
            videos_to_upload.append(entry)
    
    return videos_to_upload

def get_shortcodes_from_csv() -> Tuple[List[str], Dict[str, str]]:
    """
    Retorna shortcodes únicos e um dicionário mapeando shortcode -> link.
    Equivalente à função shortcodes_from_txt, mas lendo do CSV.
    """
    registry = load_registry()
    shortcodes = []
    shortcode_to_link = {}
    
    for sc, entry in registry.items():
        link = entry.get("insta_link", "")
        if link:  # Só inclui se tiver link
            shortcodes.append(sc)
            shortcode_to_link[sc] = link
    
    return sorted(shortcodes), shortcode_to_link