from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from rich import print
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn, TextColumn
import os, time, sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configs
USERNAME = "testemetaglass"
PASSWORD = "Alberto1812!"
CHROMEDRIVER_PATH = r"c:\Users\alber\miniconda3\envs\metaglass-env\Lib\site-packages\chromedriver_autoinstaller\142\chromedriver.exe"
TARGET_PROFILE = "testemetaglass"       # perfil alvo (sem @)
HEADLESS = True                     
DEFAULT_TIMEOUT = 20               
SCROLL_PAUSE = 1.5                  
MAX_SCROLLS = 10                   # numero de scrolls para coletar os links dos reels

INSTAGRAM = "https://www.instagram.com"


def setup_driver():
    print("⚙️  Configurando WebDriver...")
    options = ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")

    # Acelera carregamento (sem imagens/vídeos)
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.media_stream": 2,
    }
    options.add_experimental_option("prefs", prefs)

    # Evita algumas detecções simples
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(executable_path=CHROMEDRIVER_PATH)
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except WebDriverException as e:
        print(f"[bold red]❌ Erro iniciando Chrome/WebDriver:[/bold red] {e}")
        print("   → Verifique o caminho do CHROMEDRIVER_PATH e a compatibilidade com sua versão do Chrome.")
        sys.exit(1)
    print("✅ WebDriver pronto.")
    return driver

def wait_presence(driver, by, value, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        return None

def get_soup(driver):
    html = driver.page_source or ""
    if len(html) < 500:
        print("[yellow]⚠️ HTML muito curto — a página pode não ter carregado corretamente.[/yellow]")
    return BeautifulSoup(html, "html.parser")

def login(driver):
    print("🔑 Fazendo login no Instagram...")
    driver.get(INSTAGRAM + "/accounts/login/")
    # Espera inputs por NAME (mais estável). Se não achar, tenta XPaths de fallback.
    username_el = wait_presence(driver, By.NAME, "username", timeout=DEFAULT_TIMEOUT)
    password_el = wait_presence(driver, By.NAME, "password", timeout=DEFAULT_TIMEOUT)

    if not (username_el and password_el):
        # Fallback (layout alternativo)
        username_el = username_el or wait_presence(driver, By.XPATH, "//input[@name='username']")
        password_el = password_el or wait_presence(driver, By.XPATH, "//input[@name='password']")

    if not (username_el and password_el):
        print("[bold red]❌ Campos de login não encontrados. Interface pode ter mudado.[/bold red]")
        return False

    username_el.clear(); username_el.send_keys(USERNAME); time.sleep(0.3)
    password_el.clear(); password_el.send_keys(PASSWORD); time.sleep(0.3)

    # botão submit genérico
    btn = wait_presence(driver, By.XPATH, "//button[@type='submit']") or wait_presence(driver, By.CSS_SELECTOR, "button[type='submit']")
    if not btn:
        print("[bold red]❌ Botão de login não encontrado.[/bold red]")
        return False

    btn.click()
    # Aguarda redirecionar; tolera onetap/duas etapas
    with Progress(TextColumn("[bold blue]Realizando login...[/bold blue]"),
                  BarColumn(), TimeElapsedColumn(), TimeRemainingColumn(), transient=True) as progress:
        task = progress.add_task("", total=DEFAULT_TIMEOUT)
        ok = False
        for _ in range(DEFAULT_TIMEOUT):
            time.sleep(1)
            progress.update(task, advance=1)
            url = driver.current_url
            if "/accounts/onetap" in url or "instagram.com/" in url and "login" not in url:
                ok = True
                break
        if not ok:
            # ainda tenta detectar feed/home por elementos globais
            soup = get_soup(driver)
            ok = bool(soup.find("nav")) or "Save your login info" in soup.get_text()
    if ok:
        print("✅ Login efetuado.")
        # Tenta dispensar possíveis pop-ups (idioma pode variar, então só tentamos clicar botões tipo 'Not now')
        for _ in range(2):
            try:
                b = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Not Now') or contains(., 'Agora não') or contains(., 'Agora nao')]")))
                b.click(); time.sleep(1)
            except Exception:
                break
        return True
    else:
        print("[bold red]❌ Falha no login (não houve confirmação em tempo hábil).[/bold red]")
        return False

def extract_shortcode_from_url(url: str):
    """Extrai o shortcode de uma URL do Instagram."""
    try:
        path = urlparse(url.strip()).path.strip("/")
        parts = [p for p in path.split("/") if p]
        for i, p in enumerate(parts):
            if p in ("reel", "p", "tv") and i + 1 < len(parts):
                return parts[i + 1].split("?")[0].split("#")[0]
        if parts:
            return parts[-1].split("?")[0].split("#")[0] or None
    except Exception:
        pass
    return None

def extract_reel_links(html):
    """
    Extrai TODOS os links de Reels do HTML (sem filtrar).
    Retorna um dicionário {shortcode: link} para facilitar o registro.
    """
    soup = BeautifulSoup(html, "html.parser")
    links_dict = {}
    for a in soup.select("a[href*='/reel/']"):
        href = a.get("href", "")
        if "/reel/" in href:
            full = urljoin(INSTAGRAM, href)
            # normaliza sem parâmetros e com trailing slash
            full = full.split("?")[0].split("#")[0]
            if not full.endswith("/"):
                full += "/"
            
            sc = extract_shortcode_from_url(full)
            if sc:
                links_dict[sc] = full
    return links_dict

def crawl_reels(driver, profile):
    """
    Coleta TODOS os links de Reels da página (sem filtrar).
    A filtragem será feita depois, comparando com o CSV.
    """
    url = f"{INSTAGRAM}/{profile}/reels/"
    print(f"🌍 Acessando: [cyan]{url}[/cyan]")
    driver.get(url)
    time.sleep(2)

    all_links_dict = {}
    last_count = 0
    stagnant = 0
    
    with Progress(
        TextColumn("[bold magenta]Rolando e coletando links de Reels...[/bold magenta]"),
        BarColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        transient=True
    ) as progress:
        task = progress.add_task("", total=MAX_SCROLLS)
        for i in range(MAX_SCROLLS):
            # Coleta TODOS os links visíveis (sem filtrar)
            new_links = extract_reel_links(driver.page_source)
            all_links_dict.update(new_links)

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE)

            # Heurística de estagnação (nada novo em N ciclos)
            if len(all_links_dict) == last_count:
                stagnant += 1
            else:
                stagnant = 0
                last_count = len(all_links_dict)

            progress.update(task, advance=1)

            if stagnant >= 6:  # ~6 ciclos sem novidades → chega
                break

    print(f"📦 Total de links coletados da página: [green]{len(all_links_dict)}[/green]")
    return all_links_dict

def save_links(profile, links_dict):
    """
    Salva links no CSV.
    Adiciona links que não estão no CSV ou que foram removidos (status != 'downloaded').
    links_dict é um dicionário {shortcode: link}
    """
    try:
        from csv_manager import register_link, load_registry
        registry = load_registry()
        
        count_new = 0
        count_existing_downloaded = 0
        count_rediscovered = 0  # Links que estavam no CSV mas foram removidos
        
        for shortcode, link in links_dict.items():
            if shortcode not in registry:
                # Link completamente novo - adiciona
                register_link(link, shortcode)
                count_new += 1
            else:
                # Link já existe no CSV
                entry = registry[shortcode]
                status = entry.get("status", "")
                
                if status == "downloaded":
                    # Já foi baixado - mantém como está
                    count_existing_downloaded += 1
                else:
                    # Está no CSV mas não foi baixado (ou foi removido)
                    # Re-adiciona como "discovered" para passar pelo pipeline novamente
                    register_link(link, shortcode)
                    count_rediscovered += 1
        
        from csv_manager import get_csv_path
        csv_path = get_csv_path()
        print(f"💾 Links processados no CSV: [green]{csv_path}[/green]")
        print(f"   → {count_new} novos links adicionados")
        if count_rediscovered > 0:
            print(f"   → {count_rediscovered} links re-descobertos (serão processados novamente)")
        if count_existing_downloaded > 0:
            print(f"   → {count_existing_downloaded} links já baixados (mantidos)")
        return csv_path
    except Exception as e:
        print(f"[bold red]❌ Erro ao salvar links no CSV: {e}[/bold red]")
        return None

def main():
    print("\n" + "=" * 60)
    print(f"🚀 Scraper iniciado às {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

    driver = setup_driver()
    try:
        if not login(driver):
            print("[bold red]Encerrando: não foi possível logar.[/bold red]")
            return
        links = crawl_reels(driver, TARGET_PROFILE)
        save_links(TARGET_PROFILE, links)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()