from pathlib import Path
import sounddevice as sd
import numpy as np
import time
import wave

class WhatsappAudioStream:
    def __init__(self, input_device: str, output_device: str):
        self.input_device = input_device
        input_device_info = sd.query_devices(input_device, 'input')
        print("Input device info:")
        print(input_device_info)
        
        output_device_info = sd.query_devices(output_device, 'output')
        self.output_device = output_device
        print("\nOutput device info:")
        print(output_device_info)   

        self.input_sample_rate = int(input_device_info['default_samplerate'])

        self.input_channels = 2
        self.output_channels = output_device_info['max_output_channels']
        
        self.input_audio_buffer = []
    
    def record_audio_callback(self, indata, frames, time_info, status):
        self.input_audio_buffer.append(indata.copy())
    
    def verify_stop(self) -> bool:
        return False
    
    def record(self, filepath: str):
        self.input_audio_buffer = []
        
        with sd.InputStream(
            device=self.input_device,
            samplerate= self.input_sample_rate,
            channels= self.input_channels,
            callback=self.record_audio_callback,
            latency="low"
        ):
            print("Record streaming started\n")
            
            try:
                while not self.verify_stop():
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
            
            self.save_recording(filepath)
            
    def save_recording(self, filepath):
        if not self.input_audio_buffer:
            raise RuntimeError("No audio data to save.")
        
        # Concatenate all audio chunks
        audio_data = np.concatenate(self.input_audio_buffer, axis=0)
        
        # Ensure the directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save as WAV file
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.input_channels)
            wf.setsampwidth(2)  # 2 bytes for int16
            wf.setframerate(self.input_sample_rate)
            
            # Convert float32 to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())
            
    def play(self, filepath: str):
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Audio file not found: {filepath}")
        
        # Read the WAV file
        with wave.open(filepath, 'rb') as wf:
            n_channels = wf.getnchannels()
            sample_rate = wf.getframerate()
            n_frames = wf.getnframes()
            
            audio_data = wf.readframes(n_frames)
        
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Reshape to (frames, channels)
        audio_array = audio_array.reshape(-1, n_channels)
        
        # Convert to float32 (sounddevice expects float32 in range [-1.0, 1.0])
        audio_float = audio_array.astype(np.float32) / 32767.0
        
        sd.play(audio_float, samplerate=sample_rate, device=self.output_device)
        sd.wait()
        