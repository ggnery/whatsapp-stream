from pathlib import Path
import sounddevice as sd
import numpy as np
import time
import threading
from faster_whisper import WhisperModel
from scipy import signal

class WhatsappAudioStream:
    def __init__(self, input_device: str, output_device: str, 
                 model_size: str = "base", 
                 device: str = "cpu",
                 compute_type: str = "int8"):
        """
        Initialize audio stream with real-time STT capability.
        
        Args:
            input_device: Input audio device name
            output_device: Output audio device name
            model_size: Whisper model size (tiny, base, small, medium, large-v2, large-v3)
            device: cpu or cuda
            compute_type: int8, int16, float16, float32
        """
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
        
        # Audio buffers
        self.input_audio_buffer = []
        self.transcription_buffer = []
        
        # STT configuration
        self.whisper_sample_rate = 16000  # Whisper expects 16kHz
        self.chunk_duration = 2.0  # Process every 5 seconds
        self.chunk_samples = int(self.chunk_duration * self.input_sample_rate)
        
        # Initialize Whisper model
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        # Threading controls
        self.transcription_thread = None
        self.should_transcribe = False
        self.transcription_lock = threading.Lock()
        
        # Transcription results
        self.transcriptions = []  
    
    def record_audio_callback(self, indata, frames, time_info, status):
        """Callback for audio recording."""
        self.input_audio_buffer.append(indata.copy())
        
        with self.transcription_lock:
            self.transcription_buffer.append(indata.copy())
    
    def resample_audio(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate."""
        if orig_sr == target_sr:
            return audio
        
        num_samples = int(len(audio) * target_sr / orig_sr)
        resampled = signal.resample(audio, num_samples)
        return resampled
    
    def process_audio_for_whisper(self, audio_chunks: list) -> np.ndarray:
        """Convert audio chunks to format suitable for Whisper."""
        if not audio_chunks:
            return np.array([])
        
        # Concatenate chunks
        audio = np.concatenate(audio_chunks, axis=0)
        
        # Convert stereo to mono if needed
        if audio.ndim > 1 and audio.shape[1] > 1:
            audio = np.mean(audio, axis=1)
        
        # Resample to 16kHz if needed
        if self.input_sample_rate != self.whisper_sample_rate:
            audio = self.resample_audio(audio, self.input_sample_rate, self.whisper_sample_rate)
        
        audio = audio.astype(np.float32)
        
        return audio
    
    def transcription_worker(self):
        """Background thread for processing transcriptions."""
        print("Transcription worker started")
        
        while self.should_transcribe:
            time.sleep(self.chunk_duration)
            
            # Get audio chunks to process
            with self.transcription_lock:
                if len(self.transcription_buffer) == 0:
                    continue
                
                chunks_to_process = self.transcription_buffer.copy()
                self.transcription_buffer = []
            
            try:
                audio = self.process_audio_for_whisper(chunks_to_process)
                
                if len(audio) < self.whisper_sample_rate * 0.5:  # Skip if less than 0.5 seconds
                    continue
                
                # Transcribe
                segments, _ = self.model.transcribe(
                    audio,
                    beam_size=5,
                    language=None,  # Auto-detect language
                    vad_filter=True,  # Use voice activity detection
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                
                # Collect transcription
                transcription_text = ""
                for segment in segments:
                    transcription_text += segment.text + " "

                    self.transcriptions.append(transcription_text)
                    print(f"\n{transcription_text}")
                        
            except Exception as e:
                print(f"Transcription error: {e}")
        
        print("Transcription worker stopped")
    
    def verify_stop(self) -> bool:
        """Override this method to implement custom stop logic."""
        return False
    
    def record(self):
        """
        Record audio with real-time STT.

        """
        self.input_audio_buffer.clear()
        self.transcription_buffer.clear()
        self.transcriptions.clear()
        
        # Start transcription thread if enabled
        self.should_transcribe = True
        self.transcription_thread = threading.Thread(target=self.transcription_worker, daemon=True)
        self.transcription_thread.start()
        
        with sd.InputStream(
            device=self.input_device,
            samplerate=self.input_sample_rate,
            channels=self.input_channels,
            callback=self.record_audio_callback,
            latency="low"
        ):
            print("Record streaming started (press Ctrl+C to stop)")
            
            try:
                while not self.verify_stop():
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n\nStopping recording...")
            
            # Stop transcription
            self.should_transcribe = False
            self.transcription_thread.join(timeout=3.0)
            
            # Print full transcription
            print("\n" + "="*50)
            print("FULL TRANSCRIPTION:")
            print("="*50)
            for trans in self.transcriptions:
                print(trans)
            print("="*50)