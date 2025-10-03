from audio import WhatsappAudioStream
import time

INPUT_DEVICE = "CABLE-A Output (VB-Audio Virtua, MME"
OUTPUT_DEVICE ='CABLE-B Input (VB-Audio Virtual, MME'

def main():
    stream = WhatsappAudioStream(INPUT_DEVICE, OUTPUT_DEVICE)
    stream.record("test.wav")
    time.sleep(3)
    stream.play("test.wav")
    
if __name__ == "__main__":
    main()