# WhatsApp Stream

A Python application that captures audio from WhatsApp calls in real-time, transcribes speech using Whisper AI, and responds with text-to-speech using Kokoro TTS through virtual audio cables.

## Features

- **Real-time Audio Capture**: Captures audio from virtual audio cables during WhatsApp calls
- **Speech-to-Text**: Real-time transcription using OpenAI's Whisper model
- **Query Detection**: Keyword-based query capture system for interactive responses
- **Text-to-Speech**: Responds with natural speech using Kokoro TTS
- **Multi-threaded**: Runs audio capture, transcription, and query processing simultaneously
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

### System Requirements
- Python 3.12 or higher
- WhatsApp Desktop application
- Virtual Audio Cable software (for audio streaming)

### Virtual Audio Cable Setup
This application requires virtual audio cables to route WhatsApp audio. You'll need:
- **VB-Audio Virtual Cable** (recommended) or similar virtual audio cable software
- Configure the following devices:
  - `CABLE-A Output (VB-Audio Virtual)` as input device
  - `CABLE-B Input (VB-Audio Virtual)` as output device

## Installation

1. **Clone the repository**:
   ```powershell
   git clone <repository-url>
   cd whatsapp-stream
   ```

2. **Install Python dependencies (using uv)**

This project uses `pyproject.toml` and the `uv` package manager. Ensure you have Python 3.12 installed and `uv` is available on your system.

Install dependencies using `uv`:

```powershell
# Create a virtual environment
uv venv

# Activate the virtual environment (Windows PowerShell)
./.venv/Scripts/activate.ps1

# Install pip in the virtual environment
uv pip install pip

# Sync dependencies from pyproject.toml
uv sync
```



## Setup

### Audio Setup
1. Install VB-Audio Virtual Cable from [VB-Audio website](https://vb-audio.com/Cable/)
2. Configure your system audio:
   - Set WhatsApp (or the WhatsApp Desktop app) to use the virtual cable as its output device.
   - This application reads audio from the virtual cable input.
3. If your virtual audio cable devices have different names, update the device names in `audio.py` accordingly. To list available audio devices on your system, run:

```powershell
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Then set the input/output names in `audio.py` to match the device you want to use.

### WhatsApp Setup
1. Make sure WhatsApp Desktop is installed and running
2. Configure WhatsApp to use the virtual audio cable for audio output during calls

## Usage

### Run the application
```bash
python main.py
```

This will start:
1. Real-time audio capture from the configured input device
2. Continuous speech transcription using Whisper
3. Keyword-based query detection (default keyword: "banana")
4. TTS response generation using Kokoro when a query is captured

### How it works
1. The application listens for audio from your virtual audio cable
2. It transcribes speech in real-time and displays the transcription
3. When you say the keyword (e.g., "banana"), it starts recording your query
4. Say the keyword again to stop recording and process the query
5. The application generates a TTS response and plays it through the output device

### Run audio capture only
```bash
python audio.py
```

## Controls

- **Main Application**: Press `Ctrl+C` to stop audio capture and transcription
- **Query Capture**: Say your configured keyword (default: "banana") to start/stop query recording
- **Audio Stream**: Press `Ctrl+C` to stop audio streaming when running `audio.py` directly

## Configuration

### Audio Configuration
Edit the device names in `main.py` to match your virtual audio cables. Use the `sounddevice` query above to find exact device names.

Example configuration in `main.py`:

```python
INPUT_DEVICE = "CABLE-A Output (VB-Audio Virtua, MME"
OUTPUT_DEVICE = 'CABLE-B Input (VB-Audio Virtual, MME'
```

### Application Configuration
You can customize the following parameters in `main.py`:

- **start_stop_keyword**: The keyword used to start/stop query recording (default: "banana")
- **chunk_duration**: How often to process audio for transcription (default: 20.0 seconds)
- **model_size**: Whisper model size - "tiny", "base", "small", "medium", "large-v3" (default: "base")
- **device**: Processing device - "cpu" or "cuda" for GPU acceleration (default: "cpu")
- **compute_type**: Computation precision - "int8", "float16", "float32" (default: "int8")

## Troubleshooting

### Audio issues
- **"Device not found" error**:
  - Verify the virtual audio cable is installed and configured.
  - Run `python -c "import sounddevice as sd; print(sd.query_devices())"` to list available devices and use the exact device names.
  - Update device names in `main.py` to match your system.

- **No transcription appearing**:
  - Check that audio is being captured from the correct input device.
  - Ensure WhatsApp is configured to output audio to your virtual cable.
  - Verify the virtual audio cable is properly routing audio.

- **TTS not playing**:
  - Check that the output device is correctly configured.
  - Ensure the virtual audio cable output device is available and not in use by other applications.
  - Verify WhatsApp is configured to receive audio from your virtual cable input.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
