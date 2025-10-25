from audio import WhatsappAudioStream
import sounddevice as sd
from kokoro import KPipeline
import numpy as np
from scipy import signal

INPUT_DEVICE = "CABLE-A Output (VB-Audio Virtua, MME"
OUTPUT_DEVICE ='CABLE-B Input (VB-Audio Virtual, MME'

def main():
    # Uncoment to list available audio devices
    # print("Available audio devices:")
    # print(sd.query_devices())
    
    pipeline = KPipeline(lang_code='a')
    
    stream = WhatsappAudioStream(
        input_device=INPUT_DEVICE,  
        output_device=OUTPUT_DEVICE,
        start_stop_keyword="banana",
        chunk_duration=20.0,
        model_size="base",  # Options: tiny, base, small, medium, large-v3
        device="cpu",  # Use "cuda" for GPU
        compute_type="int8" 
    )
    
    query, transcriptions = stream.record()
    # Print results
    print("\n" + "="*50)
    if transcriptions:
        print("FULL TRANSCRIPTIONS:")
        print("="*50)
        print("".join(transcriptions))
    else:
        print("NO TRANSCRIPTIONS CAPTURED")
    print("="*50)
    
    # Print results
    print("\n" + "="*50)
    if query:
        print("FULL QUERY:")
        print("="*50)
        print(query)
        
        # Process query through Kokoro TTS
        try:
            generator = pipeline(query, voice='af_heart')
            # Get device info for output
            output_device_info = sd.query_devices(OUTPUT_DEVICE, 'output')
            output_sr = int(output_device_info['default_samplerate'])
            
            # Process and play each audio segment
            for i, (gs, ps, audio) in enumerate(generator):
                # Resample to match output device if needed
                if output_sr != 24000:  # Kokoro uses 24kHz
                    audio = signal.resample(audio, int(len(audio) * output_sr / 24000))
                
                # Play through output device
                sd.play(audio, output_sr, device=OUTPUT_DEVICE)
                sd.wait()  # Wait until audio is done playing
                
                print(f"Played audio segment {i+1} (gs={gs}, ps={ps})")
        except Exception as e:
            print(f"Error processing TTS: {e}")
    else:
        print("NO QUERY CAPTURED")
    print("="*50)
    
if __name__ == "__main__":
    main()