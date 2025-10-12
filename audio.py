from pathlib import Path
import sounddevice as sd
import numpy as np
import time
import threading
from faster_whisper import WhisperModel
from scipy import signal
import re

class WhatsappAudioStream:
    def __init__(self, input_device: str, output_device: str,
                 start_stop_keyword: str, 
                 chunk_duration: float,
                 model_size: str = "base", 
                 device: str = "cpu",
                 compute_type: str = "int8"):
        """
        Initialize audio stream with real-time STT capability.

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
        self.chunk_duration = chunk_duration  # Process every 5 seconds
        self.chunk_samples = int(self.chunk_duration * self.input_sample_rate)
        
        # Initialize Whisper model
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        # Threading controls
        self.should_transcribe = False
        
        self.transcription_thread = None
        self.query_thread = None
        
        self.transcription_lock = threading.Lock()    
            
        # Query
        self.start_stop_keyword = start_stop_keyword
        self.query = None  
          
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
                
                # Collect transcription - FIX: moved append outside loop
                transcription_text = ""
                for segment in segments:
                    transcription_text += segment.text + " "
                
                # Only append once per transcription cycle
                if transcription_text.strip():
                    with self.transcription_lock:
                        self.transcriptions.append(transcription_text.strip())
                    print(f"\n{transcription_text.strip()}")
                        
            except Exception as e:
                print(f"Transcription error: {e}")
        
        print("Transcription worker stopped")
    
    def keyword_in_text(self, text: str, keyword: str) -> bool:
        """Check if keyword exists as a whole word in text."""
        # Use word boundaries to match whole words only
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        return bool(re.search(pattern, text.lower()))
    
    def query_worker(self):
        """Background thread for detecting and extracting queries between keywords."""
        print("Query worker started")
        
        self.query = None
        is_recording_query = False
        current_query = []
        last_processed_index = 0
        
        while self.should_transcribe:
            time.sleep(0.3)  # Check frequently for responsiveness
            
            # Process new transcriptions with proper locking
            with self.transcription_lock:
                if last_processed_index >= len(self.transcriptions):
                    continue
                    
                # Get new transcriptions since last check
                new_transcriptions = self.transcriptions[last_processed_index:].copy()
                last_processed_index = len(self.transcriptions)
            
            # Process each new transcription
            for transcription in new_transcriptions:
                text = transcription.strip()
                
                # Use word boundary detection for keyword
                if self.keyword_in_text(text, self.start_stop_keyword):
                    if not is_recording_query:
                        # Start recording query
                        is_recording_query = True
                        current_query = []
                        print(f"\n[Query recording started]")
                    else:
                        # Stop recording query and end session
                        is_recording_query = False
                        query_text = " ".join(current_query).strip()
                        if query_text:
                            self.query = query_text
                            print(f"\n[Query captured: {self.query}]")
                        else:
                            print(f"\n[Empty query (keyword detected twice in succession)]")
                        
                        # Signal to stop recording
                        self.should_transcribe = False
                        return
                        
                elif is_recording_query:
                    # Collect text for the current query
                    if text:
                        current_query.append(text)
        
        print("Query worker stopped")
      
    def record(self):
        """
        Record audio with real-time STT and return captured query.
        """
        self.input_audio_buffer.clear()
        self.transcription_buffer.clear()
        
        with self.transcription_lock:
            self.transcriptions.clear()
        
        self.query = None  # Clear previous query
        
        # Start transcription thread
        self.should_transcribe = True
        self.transcription_thread = threading.Thread(target=self.transcription_worker, daemon=True)
        self.transcription_thread.start()
        
        # Start query detection thread
        self.query_thread = threading.Thread(target=self.query_worker, daemon=True)
        self.query_thread.start()
        
        with sd.InputStream(
            device=self.input_device,
            samplerate=self.input_sample_rate,
            channels=self.input_channels,
            callback=self.record_audio_callback,
            latency="low"
        ):
            print("Record streaming started (press Ctrl+C to stop)")
            print(f"Say '{self.start_stop_keyword}' to start/stop query capture")
            
            try:
                while self.should_transcribe:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n\nStopping recording...")
            
            # Stop transcription
            self.should_transcribe = False
            self.transcription_thread.join(timeout=3.0)
            self.query_thread.join(timeout=3.0)
            
            # Return with proper locking
            with self.transcription_lock:
                return self.query, self.transcriptions.copy()