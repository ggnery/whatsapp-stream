import subprocess
from pathlib import Path

# Configs - agora usando caminhos relativos
SOURCE_DIR = "videos"
DEST_DIR   = "audios"
OVERWRITE  = False     # True = sobrescreve; False = pula se já existir
FFMPEG_BIN = "ffmpeg"  # caminho do ffmpeg se não estiver no PATH

def ffmpeg_available():
    try:
        subprocess.run([FFMPEG_BIN, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def extract_audio_copy(input_mp4: Path, out_m4a: Path) -> bool:
    """Extrai áudio via 'stream copy' (sem re-encode) para .m4a. Retorna True se OK."""
    if out_m4a.exists() and not OVERWRITE:
        return True
    out_m4a.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG_BIN,
        "-y" if OVERWRITE else "-n",
        "-i", str(input_mp4),
        "-vn",
        "-acodec", "copy",
        str(out_m4a),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0 and out_m4a.exists() and out_m4a.stat().st_size > 0

def extract_audio_mp3(input_mp4: Path, out_mp3: Path) -> bool:
    """Fallback: re-encode para .mp3 (compatível com praticamente tudo)."""
    if out_mp3.exists() and not OVERWRITE:
        return True
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG_BIN,
        "-y" if OVERWRITE else "-n",
        "-i", str(input_mp4),
        "-vn",
        "-ac", "2",
        "-ar", "44100",
        "-b:a", "192k",
        str(out_mp3),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0 and out_mp3.exists() and out_mp3.stat().st_size > 0

def main():
    if not ffmpeg_available():
        print("❌ ffmpeg não encontrado. Instale e garanta que está no PATH.")
        return

    src = Path(SOURCE_DIR)
    dst = Path(DEST_DIR)
    dst.mkdir(parents=True, exist_ok=True)

    mp4s = sorted(src.glob("*.mp4"))
    print(f"🎬 Encontrados {len(mp4s)} vídeos em {src}")

    ok, fail, skip = 0, 0, 0
    for video in mp4s:
        base = video.stem  # ex.: "02-11-2025"
        out_m4a = dst / f"{base}.m4a"
        out_mp3 = dst / f"{base}.mp3"

        # Verifica se o áudio já existe antes de qualquer coisa
        if (out_m4a.exists() or out_mp3.exists()) and not OVERWRITE:
            # print(f"⏩ Pulando: {video.name} (áudio já existe)") # Opcional: log por arquivo
            skip += 1
            continue

        # 1) tenta copiar áudio para .m4a (sem re-encode)
        if extract_audio_copy(video, out_m4a):
            print(f"✅ {video.name} → {out_m4a.name}")
            ok += 1
            continue

        # 2) fallback: re-encode para .mp3
        if extract_audio_mp3(video, out_mp3):
            print(f"✅ {video.name} → {out_mp3.name} (fallback mp3)")
            ok += 1
        else:
            print(f"❌ Falha: {video.name}")
            fail += 1

    print(f"\nConcluído: {ok} convertidos, {fail} falhas, {skip} pulados. Áudios em: {dst.resolve()}")

if __name__ == "__main__":
    main()