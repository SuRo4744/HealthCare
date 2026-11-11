"""
Explainer Video Generation Module
Creates animated videos explaining 3D models
"""

from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
from moviepy import (
    VideoClip, TextClip, CompositeVideoClip,
    ColorClip, ImageClip, AudioClip
)
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class ExplainerVideoGenerator:
    """
    Generates explainer videos from 3D models
    Creates animated presentations with voiceover text
    """

    def __init__(self, output_dir: Path = Path("./outputs/videos")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Video settings
        self.width = 1920
        self.height = 1080
        self.fps = 30
        self.duration_per_slide = 4

    def create_title_scene(self, product_name: str, product_type: str) -> VideoClip:
        """Create opening title scene"""
        background = ColorClip(
            size=(self.width, self.height),
            color=(15, 23, 42),
            duration=3
        )

        # Create title text as PIL image for better quality
        img = Image.new('RGB', (self.width, self.height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        # Try to load font, fallback to default
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
            font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Center text
        title_text = f"{product_name}"
        subtitle_text = f"3D Model Explainer - {product_type}"

        # Calculate positions
        title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]

        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_small)
        subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]

        x_title = (self.width - title_w) // 2
        y_title = self.height // 2 - 100
        x_subtitle = (self.width - subtitle_w) // 2
        y_subtitle = self.height // 2 + 50

        draw.text((x_title, y_title), title_text, font=font_large, fill=(255, 255, 255))
        draw.text((x_subtitle, y_subtitle), subtitle_text, font=font_small, fill=(148, 163, 184))

        # Convert PIL to numpy array for moviepy
        img_array = np.array(img)

        clip = ImageClip(img_array, duration=3)
        return clip

    def create_3d_rotation_scene(self, model_path: Path, duration: float = 8) -> List[VideoClip]:
        """Create scene showing 3D model rotation"""
        clips = []

        # Check if model exists
        if not model_path.exists():
            # Create placeholder visualization
            placeholder = self.create_model_placeholder(duration)
            clips.append(placeholder)
            return clips

        # For now, create a placeholder that represents 3D rotation
        # Real 3D rendering would require Three.js or Blender integration
        placeholder = self.create_model_placeholder(duration)
        clips.append(placeholder)

        return clips

    def create_model_placeholder(self, duration: float) -> VideoClip:
        """Create placeholder for 3D model visualization"""
        # Create gradient background
        bg = ColorClip(
            size=(self.width, self.height),
            color=(30, 41, 59),
            duration=duration
        )

        # Create rotating wireframe effect using text
        img = Image.new('RGB', (self.width, self.height), color=(30, 41, 59))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        except:
            font = ImageFont.load_default()

        # Draw 3D wireframe representation
        center_x, center_y = self.width // 2, self.height // 2

        # Draw rotating box lines (simplified)
        for i in range(8):
            angle = i * 45
            x1 = center_x + int(200 * np.cos(np.radians(angle)))
            y1 = center_y + int(200 * np.sin(np.radians(angle)))
            x2 = center_x + int(200 * np.cos(np.radians(angle + 90)))
            y2 = center_y + int(200 * np.sin(np.radians(angle + 90)))
            draw.line([(x1, y1), (x2, y2)], fill=(59, 130, 246), width=3)

        draw.text((center_x - 150, center_y + 300), "3D Model Visualization",
                  font=font, fill=(226, 232, 240))

        img_array = np.array(img)
        clip = ImageClip(img_array, duration=duration)

        return CompositeVideoClip([bg, clip])

    def create_annotations_scene(self, features: List[Dict], duration_per_feature: float = 3) -> List[VideoClip]:
        """Create scenes highlighting model features"""
        clips = []

        for feature in features:
            img = Image.new('RGB', (self.width, self.height), color=(15, 23, 42))
            draw = ImageDraw.Draw(img)

            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
                body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except:
                title_font = ImageFont.load_default()
                body_font = ImageFont.load_default()

            # Draw feature annotation
            title = feature.get('title', 'Feature')
            description = feature.get('description', '')

            # Draw callout box
            box_x, box_y = 200, 300
            box_w, box_h = 1400, 400

            draw.rectangle(
                [box_x, box_y, box_x + box_w, box_y + box_h],
                fill=(30, 41, 59),
                outline=(59, 130, 246),
                width=3
            )

            draw.text((box_x + 50, box_y + 50), title, font=title_font, fill=(255, 255, 255))
            draw.text((box_x + 50, box_y + 150), description, font=body_font, fill=(148, 163, 184))

            # Draw arrow indicator
            draw.polygon(
                [(self.width // 2 + 200, self.height // 2),
                 (self.width // 2 + 250, self.height // 2 - 50),
                 (self.width // 2 + 250, self.height // 2 + 50)],
                fill=(59, 130, 246)
            )

            img_array = np.array(img)
            clip = ImageClip(img_array, duration=duration_per_feature)
            clips.append(clip)

        return clips

    def create_specs_scene(self, specs: Dict) -> VideoClip:
        """Create specifications scene"""
        img = Image.new('RGB', (self.width, self.height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 64)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        except:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()

        # Title
        draw.text((self.width // 2 - 200, 150), "Specifications",
                  font=title_font, fill=(255, 255, 255))

        # Specs
        y_offset = 300
        for key, value in specs.items():
            text = f"{key}: {value}"
            draw.text((300, y_offset), text, font=body_font, fill=(226, 232, 240))
            y_offset += 60

        img_array = np.array(img)
        clip = ImageClip(img_array, duration=4)

        return clip

    def create_closing_scene(self, duration: float = 3) -> VideoClip:
        """Create closing scene"""
        img = Image.new('RGB', (self.width, self.height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        except:
            font = ImageFont.load_default()

        text = "Scan QR code to view 3D model"
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]

        draw.text((self.width // 2 - w // 2, self.height // 2),
                  text, font=font, fill=(148, 163, 184))

        img_array = np.array(img)
        clip = ImageClip(img_array, duration=duration)

        return clip

    def generate_video(
        self,
        project_id: str,
        product_name: str,
        product_type: str,
        model_path: Optional[Path] = None,
        features: Optional[List[Dict]] = None,
        specs: Optional[Dict] = None,
        language: str = "en"
    ) -> dict:
        """
        Generate complete explainer video
        """
        print(f"Generating explainer video for {product_name}...")

        clips = []

        # 1. Title scene
        print("Creating title scene...")
        clips.append(self.create_title_scene(product_name, product_type))

        # 2. 3D model rotation
        print("Creating 3D model scenes...")
        if model_path:
            model_clips = self.create_3d_rotation_scene(model_path, duration=8)
            clips.extend(model_clips)
        else:
            clips.append(self.create_model_placeholder(8))

        # 3. Feature annotations
        if features:
            print("Creating feature annotation scenes...")
            feature_clips = self.create_annotations_scene(features)
            clips.extend(feature_clips)

        # 4. Specifications
        if specs:
            print("Creating specifications scene...")
            clips.append(self.create_specs_scene(specs))

        # 5. Closing scene
        print("Creating closing scene...")
        clips.append(self.create_closing_scene())

        # Combine all clips
        print("Rendering video...")
        final_video = CompositeVideoClip(clips)

        # Save video
        output_path = self.output_dir / f"{project_id}_explainer.mp4"
        final_video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            logger=None
        )

        # Save metadata
        metadata = {
            "project_id": project_id,
            "product_name": product_name,
            "product_type": product_type,
            "language": language,
            "created_at": datetime.utcnow().isoformat(),
            "duration_seconds": sum(clip.duration for clip in clips),
            "video_path": str(output_path),
            "resolution": f"{self.width}x{self.height}",
            "segments": len(clips)
        }

        metadata_path = self.output_dir / f"{project_id}_explainer_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Explainer video saved to {output_path}")

        return {
            "project_id": project_id,
            "video_path": str(output_path),
            "metadata_path": str(metadata_path),
            "duration": metadata["duration_seconds"],
            "status": "completed"
        }


def generate_explainer_for_project(
    project_id: str,
    product_name: str,
    product_type: str,
    model_path: Path,
    output_dir: Path
) -> dict:
    """High-level explainer video generation"""
    generator = ExplainerVideoGenerator(output_dir)

    # Default features and specs for healthcare products
    default_features = [
        {"title": "Precise Dimensions", "description": "High-accuracy 3D reconstruction from multiple angles"},
        {"title": "Surface Details", "description": "Captures fine textures and surface features"},
        {"title": "Interactive View", "description": "Rotate, zoom, and inspect from any angle"}
    ]

    default_specs = {
        "Material": "Medical-grade polymer",
        "Sterilization": "Autoclavable",
        "Compatibility": "Universal fit",
        "Weight": "Lightweight design"
    }

    result = generator.generate_video(
        project_id=project_id,
        product_name=product_name,
        product_type=product_type,
        model_path=model_path,
        features=default_features,
        specs=default_specs
    )

    return result
