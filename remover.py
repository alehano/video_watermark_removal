import cv2
import numpy as np
import argparse
import sys
import os
import shutil
import subprocess

def remove_watermarks(input_video, output_video, watermark_events):
    """
    Reads a video, removes watermarks based on a list of events, and saves the result.
    Supports different mask shapes and feathering for more natural removal.
    """
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        print(f"Error: Could not open input video: {input_video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Define the codec for the output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Use 'mp4v' for .mp4 files
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    print(f"Processing video: {input_video}")
    print(f"FPS: {fps}, Dimensions: {width}x{height}, Total Frames: {total_frames}")

    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time_sec = frame_number / fps
        processed_frame = frame.copy()

        for event in watermark_events:
            if event['start'] <= current_time_sec < event['end']:
                x, y, w, h = event['x'], event['y'], event['w'], event['h']
                shape = event.get('shape', 'ellipse')
                feather = event.get('feather', 5)
                
                # Create a mask for the watermark area
                mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                
                # Draw mask based on shape type
                if shape == 'circle':
                    # Use the smaller dimension as diameter
                    radius = min(w, h) // 2
                    center = (x + w // 2, y + h // 2)
                    cv2.circle(mask, center, radius, 255, -1)
                elif shape == 'ellipse':
                    # Ellipse fits the bounding box
                    center = (x + w // 2, y + h // 2)
                    axes = (w // 2, h // 2)
                    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
                else:  # 'rect' or default
                    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
                
                # Apply feathering (Gaussian blur) to soften edges
                if feather > 0:
                    # Make kernel size odd and proportional to feather value
                    ksize = feather * 2 + 1
                    mask = cv2.GaussianBlur(mask, (ksize, ksize), 0)

                # Apply inpainting with larger radius for better results
                processed_frame = cv2.inpaint(processed_frame, mask, 7, cv2.INPAINT_TELEA)

        out.write(processed_frame)

        frame_number += 1
        # Print progress to the console
        sys.stdout.write(f"\rProgress: {frame_number}/{total_frames} frames ({int(frame_number/total_frames*100)}%)")
        sys.stdout.flush()

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"\nProcessing complete. Video saved to: {output_video}")

def strip_audio_track(video_path: str) -> None:
    """
    Removes the audio track from the given MP4 file in-place using ffmpeg, if available.
    Falls back silently if ffmpeg is not installed.
    """
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path is None:
        # ffmpeg not available; OpenCV output is typically video-only already
        return

    base, ext = os.path.splitext(video_path)
    temp_path = f"{base}.muted{ext}"

    try:
        subprocess.run(
            [ffmpeg_path, '-y', '-i', video_path, '-c', 'copy', '-an', temp_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.replace(temp_path, video_path)
    except subprocess.CalledProcessError:
        # If muting fails, keep original file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

def copy_audio_from_source_to_target(source_video: str, target_video: str) -> None:
    """
    Attempts to copy the audio track from source_video into target_video in-place using ffmpeg.
    Keeps the existing video stream as-is. If ffmpeg is not available or if the
    source has no audio, this is a no-op.
    """
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path is None:
        return

    base, ext = os.path.splitext(target_video)
    temp_path = f"{base}.withaudio{ext}"

    # Use optional audio mapping with 'a?' so it succeeds even if input has no audio
    # -shortest ensures we don't overrun if streams differ slightly in length
    cmd = [
        ffmpeg_path,
        '-y',
        '-i', target_video,   # 0: processed (video only)
        '-i', source_video,   # 1: original (audio source)
        '-map', '0:v:0',
        '-map', '1:a?',
        '-c', 'copy',
        '-shortest',
        temp_path,
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.replace(temp_path, target_video)
    except subprocess.CalledProcessError:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

def main():
    parser = argparse.ArgumentParser(
        description="A command-line tool to remove watermarks from a video.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-i', '--input', required=True, help="Path to the input video file.")
    parser.add_argument('-o', '--output', required=True, help="Path for the output video file.")
    parser.add_argument(
        '-w', '--watermarks',
        required=True,
        nargs='+',
        help="""Watermark definition(s) in the format: 'x,y,w,h,start_sec,end_sec[,shape[,feather]]'
Shapes: 'rect', 'ellipse' (default), 'circle'
Feather: blur amount for softer edges (default: 5, 0 for sharp edges)

Examples:
-w "50,50,100,20,0,3"                    # ellipse with default feather
-w "50,50,100,20,0,3,rect"               # rectangle with default feather
-w "50,50,100,20,0,3,ellipse,10"         # ellipse with heavy feathering
-w "300,400,120,120,3,6,circle,3"        # circle with light feathering
"""
    )
    parser.add_argument(
        '--mute', '--no-audio', dest='mute', action='store_true',
        help="Ensure the output file has no audio track (uses ffmpeg if available)."
    )

    args = parser.parse_args()
    watermark_events = []
    try:
        for w_str in args.watermarks:
            parts = w_str.split(',')
            if len(parts) < 6 or len(parts) > 8:
                raise ValueError("Definition must have 6-8 comma-separated values.")
            
            # Parse numeric values
            x, y, w, h, start, end = [int(p) for p in parts[:6]]
            
            # Parse optional shape (default: 'ellipse')
            shape = parts[6].lower() if len(parts) > 6 else 'ellipse'
            if shape not in ['rect', 'ellipse', 'circle']:
                raise ValueError(f"Invalid shape '{shape}'. Must be 'rect', 'ellipse', or 'circle'.")
            
            # Parse optional feather (default: 5)
            feather = int(parts[7]) if len(parts) > 7 else 5
            if feather < 0:
                raise ValueError("Feather value must be non-negative.")
            
            event = {
                'x': x, 'y': y, 'w': w, 'h': h,
                'start': start, 'end': end,
                'shape': shape,
                'feather': feather
            }
            watermark_events.append(event)
    except (ValueError, IndexError) as e:
        print(f"Error: Invalid watermark format in '{w_str}'. Please use 'x,y,w,h,start,end[,shape[,feather]]'.")
        print(f"Details: {e}")
        return

    remove_watermarks(args.input, args.output, watermark_events)
    if args.mute:
        strip_audio_track(args.output)
    else:
        copy_audio_from_source_to_target(args.input, args.output)

if __name__ == '__main__':
    main()
