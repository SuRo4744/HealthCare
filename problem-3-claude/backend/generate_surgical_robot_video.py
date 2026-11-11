"""
Generate a synthetic sample video of a surgical robot machine
for testing the Video to 3D Model pipeline.
No real medical content - purely animated/illustrative.
"""

from pathlib import Path
from moviepy import ImageSequenceClip
import numpy as np
from PIL import Image, ImageDraw

def draw_surgical_robot(draw, center_x, center_y, angle, frame_num, total_frames):
    """Draw an animated surgical robot machine"""
    # Base platform
    draw.rectangle(
        [center_x - 120, center_y + 80, center_x + 120, center_y + 130],
        fill=(40, 50, 65), outline=(71, 85, 105), width=3
    )

    # Vertical column / main body
    col_angle = np.radians(angle * 0.5)
    col_x = center_x + int(40 * np.cos(col_angle))
    draw.rectangle(
        [col_x - 30, center_y - 100, col_x + 30, center_y + 80],
        fill=(55, 65, 80), outline=(100, 116, 140), width=3
    )

    # Robotic arm segments (animated)
    arm_base_x = col_x
    arm_base_y = center_y - 100

    # First arm segment
    seg1_angle = np.radians(angle)
    seg1_len = 80
    seg1_x = arm_base_x + int(seg1_len * np.cos(seg1_angle))
    seg1_y = arm_base_y + int(seg1_len * np.sin(seg1_angle))
    draw.line([(arm_base_x, arm_base_y), (seg1_x, seg1_y)], fill=(96, 165, 250), width=8)

    # Second arm segment
    seg2_angle = np.radians(angle * 1.3)
    seg2_len = 70
    seg2_x = seg1_x + int(seg2_len * np.cos(seg2_angle))
    seg2_y = seg1_y + int(seg2_len * np.sin(seg2_angle))
    draw.line([(seg1_x, seg1_y), (seg2_x, seg2_y)], fill=(96, 165, 250), width=8)

    # Surgical tool / end effector
    draw.ellipse([seg2_x - 15, seg2_y - 15, seg2_x + 15, seg2_y + 15],
                 fill=(30, 58, 138), outline=(147, 197, 253), width=3)
    draw.line([(seg2_x, seg2_y), (seg2_x, seg2_y + 30)],
              fill=(226, 232, 240), width=4)

    # Monitor screen on column
    screen_x = col_x - 25
    screen_y = center_y - 160
    draw.rectangle(
        [screen_x, screen_y, screen_x + 50, screen_y + 70],
        fill=(15, 23, 42), outline=(59, 130, 246), width=2
    )
    draw.text((screen_x + 8, screen_y + 10), "ROBOT", fill=(96, 165, 250))
    draw.text((screen_x + 5, screen_y + 30), "ACTIVE", fill=(34, 197, 94))

    # Control panel on base
    panel_x = center_x - 100
    panel_y = center_y + 135
    draw.rectangle(
        [panel_x, panel_y, panel_x + 60, panel_y + 25],
        fill=(30, 41, 59), outline=(71, 85, 105), width=2
    )
    draw.text((panel_x + 8, panel_y + 5), "ON", fill=(34, 197, 94))

    # Floor shadow
    draw.ellipse([center_x - 130, center_y + 200, center_x + 130, center_y + 230],
                 outline=(0, 0, 0), width=2)


def create_surgical_robot_video(output_path: Path, duration: int = 12):
    print(f"Generating {duration}-second surgical robot video at {output_path}...")

    width, height = 1920, 1080
    fps = 30
    total_frames = duration * fps

    frames = []
    for i in range(total_frames):
        img = Image.new('RGB', (width, height), color=(8, 15, 25))
        draw = ImageDraw.Draw(img)

        # Header
        draw.text((60, 40), "SURGICAL ROBOT SYSTEM - 360 WALK-AROUND", fill=(226, 232, 240))
        draw.text((60, 80), f"Frame {i+1}/{total_frames}  •  Time: {i/fps:.1f}s  •  3D Scan Ready", fill=(96, 165, 250))

        # Operating room background elements
        draw.rectangle([0, 130, width, 600], fill=(20, 30, 45))
        draw.rectangle([0, 600, width, height], fill=(12, 18, 28))

        # Draw the surgical robot
        angle = (i / total_frames) * 360
        draw_surgical_robot(draw, width // 2, height // 2 + 50, angle, i, total_frames)

        # Footer
        draw.text((60, height - 80), "ILLUSTRATIVE CONTENT - NOT REAL SURGERY", fill=(100, 116, 139))
        draw.text((60, height - 50), "For 3D Model Reconstruction Testing Only", fill=(71, 85, 105))

        frames.append(np.array(img))

    clip = ImageSequenceClip(frames, fps=fps)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    clip.write_videofile(str(output_path), codec='libx264', fps=fps, logger=None)
    print(f"Surgical robot video saved to {output_path}")


if __name__ == "__main__":
    output_dir = Path("uploads")
    output_dir.mkdir(exist_ok=True)
    sample_video_path = output_dir / "surgical_robot_walkaround.mp4"
    create_surgical_robot_video(sample_video_path, duration=12)
