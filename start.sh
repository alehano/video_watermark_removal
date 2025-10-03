#!/bin/bash

set -euo pipefail

# Always run from the project directory (location of this script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Create venv if missing
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Ensure dependencies are installed (only if cv2 is missing)
if ! python -c "import cv2" >/dev/null 2>&1; then
  echo "Installing Python dependencies..."
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

# If no arguments passed, show usage and exit
if [ $# -eq 0 ]; then
  echo "Usage: ./start.sh -i <input.mp4> -o <output.mp4> -w \"x,y,w,h,start,end\" [more ...]"
  echo "Example: ./start.sh -i input_video.mp4 -o output_video.mp4 -w \"80,30,160,66,0,3\""
  echo "Example (multiple): ./start.sh -i input.mp4 -o output.mp4 -w \"50,50,100,20,0,3\" \"300,400,120,30,3,6\""
  exit 1
fi

# Pass through any CLI args to remover.py
# Examples:
#   ./start.sh -i input.mp4 -o output.mp4 -w "50,50,100,20,0,3"
#   ./start.sh -i input.mp4 -o output.mp4 -w "50,50,100,20,0,3" "300,400,120,30,3,6"
python remover.py "$@"