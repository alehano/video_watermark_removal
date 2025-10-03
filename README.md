# Video Watermark Remover

A command-line tool to remove watermarks from videos using OpenCV's inpainting algorithm.

## Features

- Remove multiple watermarks from a single video
- Specify exact timing for each watermark appearance
- Precise coordinate-based watermark removal
- Multiple mask shapes: ellipse (default), circle, rectangle
- Feathered mask edges for smoother blending
- Configurable inpainting algorithm: TELEA (fast) or NS (higher quality)
- Multi-pass inpainting and adjustable radius for better results
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

Each watermark definition accepts 6 to 11 comma-separated values:

- `x,y,w,h,start_sec,end_sec[,shape[,feather[,algorithm[,radius[,passes]]]]]`

Where:

- `x, y`: Top-left corner coordinates of the watermark
- `w, h`: Width and height of the watermark
- `start_sec, end_sec`: Time range when the watermark appears (in seconds)
- `shape` (optional): one of `ellipse` (default), `circle`, `rect`
- `feather` (optional): edge blur amount for mask (default: 5; 0 = sharp)
- `algorithm` (optional): `telea` (default) or `ns` (Navier-Stokes)
- `radius` (optional): inpainting radius in pixels (default: 7; typical 1–25)
- `passes` (optional): number of inpainting iterations (default: 1; 1–5)

### Example Usage

For a video with three watermarks:

- **Watermark 1:** Appears from 0-3 seconds at position (50,50) with size 100x20
- **Watermark 2:** Appears from 3-6 seconds at position (300,400) with size 120x30
- **Watermark 3:** Appears from 7-10 seconds at position (500,100) with size 80x25

```bash
# Basic (default settings; ellipse shape, telea algorithm, 1 pass, radius 7)
python remover.py -i my_video.mp4 -o video_clean.mp4 -w "50,50,100,20,0,3" "300,400,120,30,3,6" "500,100,80,25,7,10"

# Rectangle mask with default feather, TELEA (fast)
python remover.py -i my_video.mp4 -o out_rect.mp4 -w "50,50,100,20,0,3,rect"

# Ellipse with heavy feathering and 2 passes, radius 10 (balanced quality)
python remover.py -i my_video.mp4 -o out_balanced.mp4 -w "50,50,100,20,0,3,ellipse,10,telea,10,2"

# Circle mask, NS algorithm, 3 passes, radius 12 (higher quality)
python remover.py -i my_video.mp4 -o out_quality.mp4 -w "300,400,120,120,3,6,circle,5,ns,12,3"

# Ensure output has no audio track (requires ffmpeg installed)
python remover.py -i my_video.mp4 -o out_muted.mp4 -w "50,50,100,20,0,3" --mute
```

### Tips

- For simple logos: keep defaults or use `telea,7,1`
- For complex/gradient watermarks: try `ns,10,2`
- For large watermarks: try `ns,12-15,2-3`
- Increase `feather` (e.g., 8–12) to reduce visible edges

### Finding Watermark Coordinates

To find the exact coordinates of watermarks in your video:

1. Use a video player like VLC to pause at the frame where the watermark appears
2. Note the pixel coordinates of the top-left corner
3. Measure the width and height of the watermark area
4. Note the time range when the watermark is visible

Alternatively, you can use OpenCV to create a simple coordinate finder script.

## How It Works

The tool uses OpenCV's `cv2.inpaint()` to fill watermark regions based on surrounding pixels.

- Algorithms:
  - `INPAINT_TELEA` (default): fast and suitable for most use-cases
  - `INPAINT_NS` (Navier-Stokes): slower but can produce smoother results
- Quality controls:
  - Feathered masks soften edges before inpainting
  - Adjustable inpainting `radius` controls neighborhood size
  - Multi-pass inpainting (`passes`) can further refine the output

## Requirements

- Python 3.7+
- OpenCV (opencv-python)
- NumPy

## Output

The processed video will be saved with the same frame rate and dimensions as the input video, but with watermarks removed from the specified areas and time ranges.
