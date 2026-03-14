#!/bin/bash
# Install TTS after Windows SDK is added

echo "Installing TTS==0.22.0..."
source venv/Scripts/activate
pip install TTS==0.22.0

if [ $? -eq 0 ]; then
    echo "✅ TTS installed successfully!"
    echo "Verifying installation..."
    python -c "from TTS.api import TTS; print('✅ TTS is working!')"
else
    echo "❌ TTS installation failed"
    echo "Make sure Windows SDK headers are installed"
    exit 1
fi
