from audio import WhatsappAudioStream
import sounddevice as sd

INPUT_DEVICE = "CABLE-A Output (VB-Audio Virtua, MME"
OUTPUT_DEVICE ='CABLE-B Input (VB-Audio Virtual, MME'

def main():
    # Uncoment to list available audio devices
    # print("Available audio devices:")
    # print(sd.query_devices())
    
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
    else:
        print("NO QUERY CAPTURED")
    print("="*50)
    
if __name__ == "__main__":
    main()