#!/bin/bash

# Video Watermark Remover Setup Script

echo "Setting up Video Watermark Remover..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To use the tool:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the remover: python remover.py -i input.mp4 -o output.mp4 -w 'x,y,w,h,start,end'"
echo ""
echo "See README.md for detailed usage instructions."
