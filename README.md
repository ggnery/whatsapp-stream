# WhatsApp Stream

A Python application that captures and streams both video and audio from WhatsApp in real-time using screen capture and virtual audio cables.

## Features

- **Real-time Video Capture**: Captures the WhatsApp window and displays it with optional processing
- **Real-time Audio Streaming**: Routes audio from virtual audio cables for WhatsApp calls
- **Multi-threaded**: Runs video and audio capture simultaneously
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
   ```bash
   git clone <repository-url>
   cd whatsapp-stream
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install additional system dependencies** (if needed):
   
   **Windows Only**:
   - Most dependencies should install automatically with pip
   - Make sure you have Microsoft Visual C++ Build Tools if compilation is needed

## Setup

### Audio Setup
1. Install VB-Audio Virtual Cable from [VB-Audio website](https://vb-audio.com/Cable/)
2. Configure your system audio:
   - Set WhatsApp to use CABLE-A as output
   - The application will route audio from CABLE-A to CABLE-B
3. If your virtual audio cable devices have different names, update the device names in `audio.py`:
   ```python
   INPUT_DEVICE = 'Your-Input-Device-Name'
   OUTPUT_DEVICE = 'Your-Output-Device-Name'
   ```

### Video Setup
1. Make sure WhatsApp Desktop is installed and running
2. The application will automatically detect the WhatsApp window

## Usage

### Run the complete application
```bash
python main.py
```

This will start both video capture and audio streaming in separate threads.

### Run components separately

**Video capture only**:
```bash
python video.py
```

**Audio streaming only**:
```bash
python audio.py
```

## Controls

- **Video Window**: Press `q` to quit the video capture
- **Audio Stream**: Press `Ctrl+C` to stop audio streaming
- **Main Application**: Press `Ctrl+C` to stop both video and audio

## Configuration

### Audio Configuration
Edit the device names in `audio.py` if your virtual audio cables have different names:
```python
INPUT_DEVICE = 'CABLE-A Output (VB-Audio Virtual, MME'
OUTPUT_DEVICE = 'CABLE-B Input (VB-Audio Virtual, MME'
```

### Video Configuration
The video capture automatically detects the WhatsApp window. The application shows:
- Original WhatsApp window capture
- Processed grayscale version

## Troubleshooting

### Audio Issues
- **"Device not found" error**: 
  - Check that virtual audio cables are properly installed
  - Run `python -c "import sounddevice as sd; print(sd.query_devices())"` to list available devices
  - Update device names in `audio.py` to match your system

### Video Issues
- **"WhatsApp window not found" error**:
  - Make sure WhatsApp Desktop is running and visible
  - The window title should contain only "WhatsApp" call


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
