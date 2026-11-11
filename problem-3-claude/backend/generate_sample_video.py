"""
Script to generate a sample 10-second video of a rotating medical implant
for testing the Video to 3D Model pipeline.
"""

from pathlib import Path
from moviepy import ColorClip, TextClip, CompositeVideoClip
import numpy as np
from PIL import Image, ImageDraw

def create_sample_medical_video(output_path: Path, duration: int = 10):
    print(f"Generating {duration}-second sample medical video at {output_path}...")

    width, height = 1280, 720
    fps = 30

    # Background clip - dark medical blue
    bg = ColorClip(size=(width, height), color=(15, 23, 42), duration=duration)

    # Generate frames with a rotating 3D-like object representation
    frames = []
    total_frames = duration * fps

    for i in range(total_frames):
        img = Image.new('RGB', (width, height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        # Draw title
        draw.text((50, 50), "SAMPLE SURGICAL IMPLANT - 360 WALK-AROUND", fill=(148, 163, 184))
        draw.text((50, 80), f"Frame {i+1}/{total_frames} (Time: {i/fps:.1f}s)", fill=(96, 165, 250))

        # Rotating geometric object representing medical implant
        center_x, center_y = width // 2, height // 2
        angle = (i / total_frames) * 360

        # Draw rotating wireframe shape
        points = []
        for j in range(6):
            rad = np.radians(angle + j * 60)
            x = center_x + int(150 * np.cos(rad))
            y = center_y + int(150 * np.sin(rad))
            points.append((x, y))

        # Draw polygon / implant shape
        draw.polygon(points, outline=(59, 130, 246), width=4)
        draw.ellipse([center_x - 40, center_y - 40, center_x + 40, center_y + 40], fill=(30, 58, 138), outline=(96, 165, 250), width=2)

        # Center text
        draw.text((center_x - 120, center_y + 180), "Medical Device Demonstration", fill=(255, 255, 255))

        frames.append(np.array(img))

    from moviepy import ImageSequenceClip
    clip = ImageSequenceClip(frames, fps=fps)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    clip.write_videofile(str(output_path), codec='libx264', fps=fps, logger=None)
    print(f"Sample video saved to {output_path}")

if __name__ == "__main__":
    output_dir = Path("uploads")
    output_dir.mkdir(exist_ok=True)
    sample_video_path = output_dir / "sample_surgical_implant.mp4"
    create_sample_medical_video(sample_video_path, duration=10)
