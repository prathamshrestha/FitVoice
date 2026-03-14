# FitVoice TTS Installation Guide

## Current Status
- ✅ webrtcvad is installed via `webrtcvad-wheels==2.0.14`
- ❌ TTS requires C++ build tools (currently not available)

## Installing TTS

TTS requires Microsoft C++ Build Tools. You have two options:

### Option 1: Install C++ Build Tools (Recommended)

1. Download Microsoft C++ Build Tools from:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. Run the installer and select:
   - "Desktop development with C++"
   - Include Windows SDK (10.0 or higher)

3. After installation, restart your terminal and run:
   ```bash
   source venv/Scripts/activate
   pip install TTS==0.22.0
   ```

### Option 2: Use Pre-built Alternative
If you can't install build tools, you can use the existing dependencies without TTS for now.

### Option 3: Install using Conda
If you prefer using conda:
```bash
conda create -n fitvoice python=3.11
conda activate fitvoice
conda install -c conda-forge tts
pip install -r requirements.txt --skip-installed
```

## Verification
Once installed, verify TTS works:
```bash
python -c "from TTS.api import TTS; print('TTS installed successfully')"
```
