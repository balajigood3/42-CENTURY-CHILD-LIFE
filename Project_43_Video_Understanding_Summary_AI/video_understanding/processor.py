"""Bounded video inspection and keyframe extraction using OpenCV."""
from __future__ import annotations
from pathlib import Path
import tempfile, os

MAX_VIDEO_BYTES = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

def validate_video(filename: str, data: bytes) -> None:
    if not isinstance(data, bytes):
        raise TypeError("Video content must be bytes.")
    if not data:
        raise ValueError("Video file is empty.")
    if len(data) > MAX_VIDEO_BYTES:
        raise ValueError("Video exceeds the 100 MB upload limit.")
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported video format.")

def sample_timestamps(duration_seconds: float, max_frames: int = 6) -> list[float]:
    if duration_seconds <= 0:
        return []
    if max_frames < 1:
        raise ValueError("max_frames must be at least 1.")
    count = min(max_frames, max(1, int(duration_seconds) + 1))
    if count == 1:
        return [0.0]
    return [round(i * duration_seconds / (count - 1), 3) for i in range(count)]

def inspect_video(filename: str, data: bytes, max_frames: int = 6) -> dict:
    validate_video(filename, data)
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Install opencv-python-headless to process videos.") from exc

    suffix = Path(filename).suffix.lower()
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            temp_path = tmp.name
        cap = cv2.VideoCapture(temp_path)
        if not cap.isOpened():
            raise ValueError("Could not open video. Check codec and file integrity.")
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        duration = frame_count / fps if fps > 0 and frame_count > 0 else 0.0
        timestamps = sample_timestamps(duration, max_frames)
        frames = []
        for timestamp in timestamps:
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            ok, frame = cap.read()
            if not ok:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append({"timestamp": timestamp, "frame": frame})
        cap.release()
        if not frames:
            raise ValueError("No frames could be extracted from this video.")
        return {
            "filename": Path(filename).name,
            "duration_seconds": round(duration, 2),
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "sampled_frames": frames,
            "sampled_frame_count": len(frames),
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

def caption_frames(frames: list[dict], use_blip: bool = False) -> list[dict]:
    """Optionally caption sampled frames with a local BLIP model."""
    output = []
    processor = model = None
    note = ""
    if use_blip:
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            import torch
            model_name = os.getenv("BLIP_MODEL", "Salesforce/blip-image-captioning-base")
            processor = BlipProcessor.from_pretrained(model_name)
            model = BlipForConditionalGeneration.from_pretrained(model_name)
        except ImportError:
            note = "Optional captioning requires transformers and torch."
        except Exception as exc:
            note = f"Could not load BLIP model: {exc}"
    for item in frames:
        caption = ""
        if model is not None:
            from PIL import Image
            import torch
            image = Image.fromarray(item["frame"])
            inputs = processor(image, return_tensors="pt")
            with torch.no_grad():
                tokens = model.generate(**inputs, max_new_tokens=40)
            caption = processor.decode(tokens[0], skip_special_tokens=True)
        output.append({"timestamp": item["timestamp"], "caption": caption})
    return {"captions": output, "note": note}
