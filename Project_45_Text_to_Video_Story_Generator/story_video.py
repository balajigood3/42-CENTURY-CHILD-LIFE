"""Create a simple caption-based MP4 story video using local rendering."""
from __future__ import annotations
import re
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
PALETTES = {
    "Midnight": ((12, 18, 42), (53, 40, 91)),
    "Sunrise": ((78, 36, 48), (236, 145, 74)),
    "Forest": ((10, 48, 42), (73, 111, 70)),
    "Ocean": ((5, 42, 73), (30, 130, 155)),
}

def parse_story(story: str, max_scenes: int = 8) -> list[str]:
    if not isinstance(story, str) or not story.strip():
        raise ValueError("Story cannot be empty.")
    if max_scenes < 1 or max_scenes > 20:
        raise ValueError("max_scenes must be between 1 and 20.")
    chunks = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", story.strip()) if part.strip()]
    if not chunks:
        raise ValueError("No scenes could be extracted from the story.")
    return chunks[:max_scenes]

def _font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()

def _gradient(size, top, bottom):
    width, height = size
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(int(top[i] * (1-ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, width, y), fill=color)
    return image

def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def create_frame(scene: str, title: str, index: int, total: int,
                 style: str = "Midnight", width: int = DEFAULT_WIDTH,
                 height: int = DEFAULT_HEIGHT) -> Image.Image:
    if style not in PALETTES:
        raise ValueError(f"Unknown visual style: {style}")
    image = _gradient((width, height), *PALETTES[style])
    draw = ImageDraw.Draw(image)
    title_font = _font(42)
    body_font = _font(48)
    small_font = _font(25)
    draw.rounded_rectangle((70, 65, width-70, height-65), radius=30,
                           outline=(235, 235, 245), width=3)
    draw.text((110, 105), title[:70], font=title_font, fill=(255, 230, 170))
    draw.line((110, 170, width-110, 170), fill=(220, 220, 235), width=2)
    lines = _wrap_text(draw, scene, body_font, width-260)
    line_height = 68
    total_height = len(lines) * line_height
    y = max(220, (height-total_height)//2)
    for line in lines:
        draw.text((130, y), line, font=body_font, fill=(255, 255, 255))
        y += line_height
    draw.text((width-240, height-125), f"SCENE {index}/{total}", font=small_font,
              fill=(230, 230, 240))
    return image

def render_video(scenes: list[str], title: str = "My Story", seconds_per_scene: int = 4,
                 style: str = "Midnight", fps: int = 12) -> bytes:
    if not scenes:
        raise ValueError("At least one scene is required.")
    if seconds_per_scene < 1 or seconds_per_scene > 30:
        raise ValueError("seconds_per_scene must be between 1 and 30.")
    if fps < 1 or fps > 30:
        raise ValueError("fps must be between 1 and 30.")
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name
    try:
        writer = imageio.get_writer(output_path, fps=fps, codec="libx264",
                                    quality=7, macro_block_size=16)
        try:
            for index, scene in enumerate(scenes, 1):
                frame = create_frame(scene, title, index, len(scenes), style)
                frame_array = __import__("numpy").array(frame)
                for _ in range(seconds_per_scene * fps):
                    writer.append_data(frame_array)
        finally:
            writer.close()
        return Path(output_path).read_bytes()
    finally:
        Path(output_path).unlink(missing_ok=True)
