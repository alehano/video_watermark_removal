# Video Watermark Remover

A command-line tool to remove watermarks from videos using OpenCV's inpainting algorithm.

## Features

- Remove multiple watermarks from a single video
- Specify exact timing for each watermark appearance
- Precise coordinate-based watermark removal
- Progress tracking during processing
- Support for various video formats

## Installation

1. **Set up a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Command Structure

```bash
python remover.py -i <input_video> -o <output_video> -w <watermark_definitions>
```

### Watermark Definition Format

Each watermark is defined using 6 comma-separated values:

- `x,y,w,h,start_sec,end_sec`

Where:

- `x, y`: Top-left corner coordinates of the watermark
- `w, h`: Width and height of the watermark
- `start_sec, end_sec`: Time range when the watermark appears (in seconds)

### Example Usage

For a video with three watermarks:

- **Watermark 1:** Appears from 0-3 seconds at position (50,50) with size 100x20
- **Watermark 2:** Appears from 3-6 seconds at position (300,400) with size 120x30
- **Watermark 3:** Appears from 7-10 seconds at position (500,100) with size 80x25

```bash
python remover.py --input my_video.mp4 --output video_clean.mp4 --watermarks "50,50,100,20,0,3" "300,400,120,30,3,6" "500,100,80,25,7,10"
```

### Finding Watermark Coordinates

To find the exact coordinates of watermarks in your video:

1. Use a video player like VLC to pause at the frame where the watermark appears
2. Note the pixel coordinates of the top-left corner
3. Measure the width and height of the watermark area
4. Note the time range when the watermark is visible

Alternatively, you can use OpenCV to create a simple coordinate finder script.

## How It Works

The tool uses OpenCV's `cv2.inpaint()` function with the `INPAINT_TELEA` algorithm to intelligently fill in the watermark areas by analyzing surrounding pixels. This creates a natural-looking result that blends with the background.

## Requirements

- Python 3.7+
- OpenCV (opencv-python)
- NumPy

## Output

The processed video will be saved with the same frame rate and dimensions as the input video, but with watermarks removed from the specified areas and time ranges.
