from audio import WhatsappAudioStream
import sounddevice as sd
from kokoro import KPipeline
import numpy as np
from scipy import signal
from dotenv import load_dotenv
import os

# Import RAG and logger modules
from rag_module import RAGLocal
from logger import log_conversation

# Load environment variables
load_dotenv()

INPUT_DEVICE = "CABLE-A Output (VB-Audio Virtua, MME"
OUTPUT_DEVICE = 'CABLE-B Input (VB-Audio Virtual, MME'

# Default error message
DEFAULT_ERROR_MESSAGE = "Desculpe, não consegui processar sua pergunta. Por favor, tente novamente."
NO_INFO_MESSAGE = "Não encontrei informação sobre isso no documento."


def play_tts_response(text: str, pipeline, output_device: str):
    """
    Args:
        text: Text to convert to speech
        pipeline: Kokoro TTS pipeline
        output_device: Audio output device name
    """
    try:
        generator = pipeline(text, voice='af_heart')
        # Get device info for output
        output_device_info = sd.query_devices(output_device, 'output')
        output_sr = int(output_device_info['default_samplerate'])

        # Process and play each audio segment
        for i, (gs, ps, audio) in enumerate(generator):
            # Resample to match output device if needed
            if output_sr != 24000:  # Kokoro uses 24kHz
                audio = signal.resample(audio, int(
                    len(audio) * output_sr / 24000))

            # Play through output device
            sd.play(audio, output_sr, device=output_device)
            sd.wait()  # Wait until audio is done playing

            print(f"✓ Played audio segment {i+1} (gs={gs}, ps={ps})")
    except Exception as e:
        print(f"✗ Error processing TTS: {e}")


def main():
    # Uncoment to list available audio devices
    # print("Available audio devices:")
    # print(sd.query_devices())

    print("\n" + "="*70)
    print("SMART GLASSES - Sistema Integrado WhatsApp + RAG")
    print("="*70)

    # Initialize TTS pipeline
    print("\n[1/3] Inicializando pipeline TTS...")
    pipeline = KPipeline(lang_code='a')
    print("✓ Pipeline TTS pronto")

    # Initialize RAG system
    print("\n[2/3] Inicializando sistema RAG...")
    try:
        # Path local - documento dentro de whatsapp-stream/documents/
        pdf_path = os.path.join(os.path.dirname(
            __file__), "documents", "Xadrez.pdf")

        if not os.path.exists(pdf_path):
            print(f"✗ ERRO: PDF não encontrado em {pdf_path}")
            print(
                "Certifique-se de que o arquivo Xadrez.pdf está em whatsapp-stream/documents/")
            return

        rag = RAGLocal("Xadrez", pdf_path)
        rag.load_index()  # Agora cria o índice automaticamente se não existir
        print("✓ Sistema RAG pronto (documento: Xadrez.pdf)")
    except Exception as e:
        print(f"✗ ERRO ao inicializar RAG: {e}")
        import traceback
        traceback.print_exc()
        return

    # Initialize audio stream
    print("\n[3/3] Inicializando captura de áudio...")
    stream = WhatsappAudioStream(
        input_device=INPUT_DEVICE,
        output_device=OUTPUT_DEVICE,
        start_stop_keyword="jarvis",
        chunk_duration=20.0,
        model_size="base",  # Options: tiny, base, small, medium, large-v3
        device="cpu",  # Use "cuda" for GPU
        compute_type="int8"
    )
    print("✓ Captura de áudio pronta")

    print("\n" + "="*70)
    print("Sistema pronto! Aguardando captura de voz...")
    print("="*70 + "\n")

    # Record audio and capture query
    query, transcriptions = stream.record()

    # Print transcriptions
    print("\n" + "="*70)
    if transcriptions:
        print("TRANSCRIÇÕES COMPLETAS:")
        print("="*70)
        print("".join(transcriptions))
    else:
        print("NENHUMA TRANSCRIÇÃO CAPTURADA")
    print("="*70)

    # Process query
    print("\n" + "="*70)
    if query:
        print("QUERY CAPTURADA:")
        print("="*70)
        print(f"→ {query}")
        print("="*70)

        # Process query through RAG
        response_text = None
        is_error = False

        try:
            print("\n[RAG] Processando query...")
            result = rag.ask_question(query)
            response_text = result["answer"]

            # Check if RAG couldn't find information
            if any(phrase in response_text.lower() for phrase in
                   ["não encontrei", "não sei", "não tenho informação", "não há informação"]):
                print("[RAG] ⚠ RAG não encontrou informação relevante")
                response_text = NO_INFO_MESSAGE
            else:
                print("[RAG] ✓ Resposta gerada com sucesso")

        except Exception as e:
            print(f"[RAG] ✗ Erro ao processar query: {e}")
            response_text = DEFAULT_ERROR_MESSAGE
            is_error = True

        # Print response
        print("\n" + "-"*70)
        print("RESPOSTA:")
        print("-"*70)
        print(response_text)
        print("-"*70)

        # Log conversation
        log_conversation(query, response_text, error=is_error)

        # Generate and play TTS response
        print("\n[TTS] Gerando resposta em áudio...")
        play_tts_response(response_text, pipeline, OUTPUT_DEVICE)

    else:
        print("NENHUMA QUERY CAPTURADA")
        print("="*70)

    print("\n" + "="*70)
    print("Sessão finalizada!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
