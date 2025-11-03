import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import assemblyai as aai
import google.generativeai as genai

# Configs - agora usando caminhos relativos
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "audios"
OUTPUT_DIR = BASE_DIR / "transcriptions"
AUDIO_EXTS = {".mp3", ".m4a"}

# Utils
def hhmmss_from_ms(ms: int) -> str:
    s = int(ms // 1000)
    return str(timedelta(seconds=s))

def sanitize_md(text: str) -> str:
    return text.replace("\r\n", "\n").strip()

def make_markdown(title: str, transcript_md: str, resumo: str, bullets: str) -> str:
    bullets = bullets.strip()
    if "\n-" not in bullets and not bullets.startswith("- "):
        bullets = "\n".join(f"- {line.strip()}" for line in bullets.splitlines() if line.strip())
    tpl = f"""# {title}

## Transcrição (com falantes e timestamps)
{transcript_md}

## Resumo detalhado
{resumo.strip()}

## Pontos principais
{bullets}
"""
    return tpl

def collect_audios(input_dir: Path):
    files = []
    for ext in AUDIO_EXTS:
        files.extend(input_dir.glob(f"*{ext}"))
    return sorted(files)

# Prompts
PROMPT_RESUMO = """\
Sua tarefa é criar um resumo detalhado e coeso da transcrição de áudio fornecida.

Instruções Importantes:
1.  Analise o diálogo para inferir os papéis ou nomes dos participantes (ex: Entrevistador, Convidado, etc.) com base no contexto.
2.  No resumo final, NÃO use os termos genéricos "Falante A" ou "Falante B". Em vez disso, use os papéis ou nomes que você inferiu, ou descreva as ideias de forma impessoal.
3.  O foco principal deve ser nos tópicos, histórias e insights discutidos.

Transcrição para Análise:
---
{texto}
---
"""

PROMPT_BULLETS = """\
Extraia os principais insights e pontos de destaque da transcrição a seguir em formato de bullet points (tópicos).

Instruções:
-   Formule cada ponto com base na ideia central discutida.
-   Seja direto e informativo.
-   NÃO inicie os tópicos com "Falante A disse..." ou "Falante B falou...". Foque na informação em si.

Transcrição para Análise:
---
{texto}
---
"""

# Gemini (resumo + bullets)
def gerar_conteudo_com_gemini(model, texto_transcrito: str):
    if not texto_transcrito:
        return "N/A", "- N/A"
    texto = texto_transcrito if len(texto_transcrito) < 600_000 else texto_transcrito[:600_000]
    resp1 = model.generate_content(PROMPT_RESUMO.format(texto=texto))
    resumo_detalhado = (resp1.text or "N/A")
    resp2 = model.generate_content(PROMPT_BULLETS.format(texto=texto))
    bullet_points = (resp2.text or "- N/A")
    return resumo_detalhado, bullet_points

# AssemblyAI (transcrição)
def transcrever_arquivo(aai_transcriber, audio_path: Path):
    config = aai.TranscriptionConfig(
        language_code="pt",
        speaker_labels=True,
    )
    transcript = aai_transcriber.transcribe(str(audio_path), config)
    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"Erro na transcrição: {transcript.error}")

    if transcript.status == aai.TranscriptStatus.completed:
        if transcript.utterances:
            lines = []
            for u in transcript.utterances:
                t = hhmmss_from_ms(u.start)
                lines.append(f"[{t}] Falante {u.speaker}: {u.text}")
            diarized_text_for_llm = "\n".join(lines)
            transcript_md = sanitize_md(diarized_text_for_llm)
        else:
            transcript_md = sanitize_md(transcript.text or "")
    else:
        raise RuntimeError("Transcrição não foi completada com sucesso.")

    return transcript_md, transcript_md  # usamos o mesmo texto diarizado no LLM

# Pipeline
def process_audio(aai_transcriber, gemini_model, audio_path: Path, out_dir: Path):
    print(f"→ Processando: {audio_path.name}")
    transcript_md, llm_text = transcrever_arquivo(aai_transcriber, audio_path)
    resumo, bullets = gerar_conteudo_com_gemini(gemini_model, llm_text)
    title = audio_path.stem
    md = make_markdown(title, transcript_md, resumo, bullets)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{title}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"✅ Salvo: {out_path}")

def main():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Pasta de entrada não existe: {INPUT_DIR}")

    load_dotenv()
    ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not ASSEMBLYAI_API_KEY or not GEMINI_API_KEY:
        raise RuntimeError("Defina ASSEMBLYAI_API_KEY e GEMINI_API_KEY no .env (ou variáveis de ambiente).")

    aai.settings.api_key = ASSEMBLYAI_API_KEY
    genai.configure(api_key=GEMINI_API_KEY)

    transcriber = aai.Transcriber()
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")

    audios = collect_audios(INPUT_DIR)
    print(f"🎧 Encontrados {len(audios)} arquivos de áudio em '{INPUT_DIR}'.")

    processed_count = 0
    skipped_count = 0
    for audio_path in audios:
        # Verifica se o arquivo .md correspondente já existe
        expected_md_path = OUTPUT_DIR / f"{audio_path.stem}.md"
        if expected_md_path.exists():
            print(f"⏩ Pulando: {audio_path.name} (documento já existe)")
            skipped_count += 1
            continue

        try:
            process_audio(transcriber, gemini_model, audio_path, OUTPUT_DIR)
            processed_count += 1
        except Exception as e:
            print(f"❌ Falha em {audio_path.name}: {e}")

    print(f"\nConcluído. {processed_count} novos áudios processados, {skipped_count} pulados.")
    print(f"Markdown salvo em: {OUTPUT_DIR.resolve()}")

if __name__ == "__main__":
    main()