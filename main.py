import subprocess
import sys
from pathlib import Path
import os 

def run_script(script_name: str):
    """Executa um script Python e verifica o resultado."""
    script_path = Path(__file__).parent / script_name
    if not script_path.exists():
        print(f"❌ Erro: Script '{script_name}' não encontrado em '{script_path}'.")
        return False

    print(f"\n>>> {script_name}") # Mensagem de início mais limpa

    try:
        # Configura o ambiente para forçar a saída em UTF-8, resolvendo erros de emoji
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        # Usamos sys.executable para garantir que estamos usando o mesmo interpretador Python
        process = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,        
            capture_output=True, 
            text=True,        
            encoding='utf-8',
            errors='replace', 
            env=env            # Passa o ambiente configurado para o subprocesso
        )
        print(f"✅ Sucesso: execução finalizada.")

        if process.stdout:
            output_lines = process.stdout.strip().split('\n')
            summary_lines = []

            # Lógica para extrair a saída específica de cada script
            if script_name == "scraper-reels.py":
                summary_lines = [line for line in output_lines if "Total de links" in line or "Links processados" in line]
            elif script_name in ["download-reels.py", "video-to-audio.py"]:
                summary_lines = [line for line in output_lines if line.strip().startswith("Concluído:")]
            elif script_name == "doc-generator.py":
                summary_lines = [line for line in output_lines if line.strip().startswith("Concluído.") or "Markdown" in line]
            elif script_name == "youtube_workflow.py":
                summary_lines = [line for line in output_lines if "[YouTubeWorkflow] Processamento concluído!" in line or "Sucesso:" in line or "Falhas:" in line]
            elif script_name == "gemini_summary.py":
                summary_lines = [line for line in output_lines if "[GeminiSummary] Processamento concluído!" in line or "Sucesso:" in line or "Falhas:" in line]
            elif script_name == "pdf_generator.py":
                summary_lines = [line for line in output_lines if "[PDFGenerator] Processamento concluído!" in line or "PDFs gerados:" in line]

            # Se encontrarmos linhas específicas, imprimimos sem as bordas
            if summary_lines:
                print('\n'.join(summary_lines))
            # Se não, como fallback, mostramos as últimas 2 linhas com bordas
            else:
                fallback_lines = [line for line in output_lines if line.strip()][-2:]
                if fallback_lines:
                    print("--------------------------")
                    print('\n'.join(fallback_lines))
                    print("--------------------------")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO ao executar {script_name}:")
        print("--- Erro Padrão (stderr) ---")
        print(e.stderr)
        print("--------------------------")
        print("--- Saída Padrão (stdout) ---")
        print(e.stdout)
        print("---------------------------")
        return False
    except FileNotFoundError:
        print(f"❌ Erro: O comando '{sys.executable}' não foi encontrado. Verifique sua instalação do Python.")
        return False
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado ao executar {script_name}: {e}")
        return False

def main():
    """Pipeline de execução sequencial dos scripts."""
    scripts_para_executar = [
        "scraper-reels.py",
        "download-reels.py",
        "video-to-audio.py",
        "doc-generator.py",
        "youtube_workflow.py",
        "gemini_summary.py",
        "pdf_generator.py",
    ]

    print("Iniciando o pipeline de processamento de reels")

    for script in scripts_para_executar:
        if not run_script(script):
            print(f"\nPipeline interrompido devido a um erro em '{script}'.")
            break
    else: # Este else pertence ao for, e só executa se o loop completar sem break
        print("\nPipeline concluído com sucesso!")

if __name__ == "__main__":
    main()