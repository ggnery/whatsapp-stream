import sounddevice as sd
import time

INPUT_DEVICE = 'CABLE-A Output (VB-Audio Virtua, MME'
OUTPUT_DEVICE ='CABLE-B Input (VB-Audio Virtual, MME'

def audio_callback(indata, outdata, frames, time, status):
    """Callback function to handle real-time audio streaming"""
    if status:
        print(f"Audio callback status: {status}")
    # Copy input data directly to output
    outdata[:] = indata

def get_whatsapp_audio():
    try:
        # Get input device info
        input_device_info = sd.query_devices(INPUT_DEVICE, 'input')
        print("Input device info:")
        print(input_device_info)
        
        # Get output device info  
        output_device_info = sd.query_devices(OUTPUT_DEVICE, 'output')
        print("\nOutput device info:")
        print(output_device_info)
        
        sample_rate = int(input_device_info['default_samplerate'])
        input_channels = input_device_info['max_input_channels']
        output_channels = min(input_channels, output_device_info['max_output_channels'])
        
        print(f"\nInput device '{INPUT_DEVICE}' found.")
        print(f"Output device: {output_device_info['name']}")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Input channels: {input_channels}, Output channels: {output_channels}")
        print("Starting real-time audio streaming...")
        print("Press Ctrl+C to stop streaming.")
        
        # Create duplex stream for real-time audio
        with sd.Stream(
            device=(INPUT_DEVICE, OUTPUT_DEVICE),
            samplerate=sample_rate,
            channels=(input_channels, output_channels),
            callback=audio_callback,
            latency='low'
        ):
            print("Streaming started. Audio is now being streamed in real-time.")
            try:
                while True:
                    time.sleep(0.1)  # Keep the main thread alive
            except KeyboardInterrupt:
                print("\nStopping audio stream...")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Available devices:")
        print(sd.query_devices())
        
if __name__ == "__main__":
    get_whatsapp_audio()