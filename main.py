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
        model_size="base",  # Options: tiny, base, small, medium, large-v3
        device="cpu",  # Use "cuda" for GPU
        compute_type="int8" 
    )
    
    stream.record()
    
if __name__ == "__main__":
    main()