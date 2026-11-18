"""Image validation and question answering using optional local BLIP."""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageStat
import io

MAX_IMAGE_BYTES = 15 * 1024 * 1024
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
_MAX_PIXELS = 25_000_000

def validate_image(filename: str, size: int) -> None:
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported image format. Use PNG, JPG, JPEG, WEBP, or BMP.")
    if size <= 0:
        raise ValueError("The uploaded image is empty.")
    if size > MAX_IMAGE_BYTES:
        raise ValueError("Image exceeds the 15 MB upload limit.")

def _image_details(image: Image.Image) -> dict:
    width, height = image.size
    if width * height > _MAX_PIXELS:
        raise ValueError("Image dimensions are too large to process safely.")
    rgb = image.convert("RGB")
    means = ImageStat.Stat(rgb.resize((min(width, 256), min(height, 256))).convert("RGB")).mean
    dominant = max(zip(("red", "green", "blue"), means), key=lambda pair: pair[1])[0]
    return {
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 3) if height else None,
        "dominant_average_channel": dominant,
        "average_rgb": [round(x, 1) for x in means],
    }

def _blip_answer(image: Image.Image, question: str) -> str:
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError(
            "BLIP mode requires optional packages. Install with: "
            "pip install transformers torch. Then retry, or select Basic image analysis."
        ) from exc
    # Cached after the first invocation within this Python process.
    global _BLIP_PIPELINE
    try:
        pipe = _BLIP_PIPELINE
    except NameError:
        _BLIP_PIPELINE = pipeline(
            "visual-question-answering",
            model="Salesforce/blip-vqa-base",
            device=-1,
        )
        pipe = _BLIP_PIPELINE
    outputs = pipe(image, question=question)
    if not outputs:
        return "The model did not return an answer."
    return str(outputs[0].get("answer", "No answer returned."))

def answer_question(image: Image.Image, question: str, mode: str = "Automatic") -> dict:
    if image is None:
        raise ValueError("Please provide an image.")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a question.")
    if mode not in {"Automatic", "Local BLIP model", "Basic image analysis"}:
        raise ValueError("Unknown answering mode.")
    details = _image_details(image)
    if mode in {"Automatic", "Local BLIP model"}:
        try:
            answer = _blip_answer(image.convert("RGB"), question.strip())
            return {
                "answer": answer,
                "method": "Local BLIP VQA",
                "confidence_note": "Model-generated answer; verify important details.",
                "details": details,
            }
        except RuntimeError:
            if mode == "Local BLIP model":
                raise
        except Exception as exc:
            if mode == "Local BLIP model":
                raise RuntimeError(f"BLIP inference failed: {exc}") from exc

    q = question.casefold()
    if any(term in q for term in ("width", "wide", "pixels across")):
        answer = f"The image is {details['width']} pixels wide."
    elif any(term in q for term in ("height", "tall", "pixels high")):
        answer = f"The image is {details['height']} pixels high."
    elif "aspect ratio" in q:
        answer = f"The image aspect ratio is {details['aspect_ratio']}."
    elif "color" in q or "colour" in q:
        answer = f"The strongest average RGB channel is {details['dominant_average_channel']}."
    else:
        answer = (
            "Basic mode can report image dimensions and average color statistics, "
            "but cannot reliably identify objects or understand scene content. "
            "Install the local BLIP model for visual question answering."
        )
    return {
        "answer": answer,
        "method": "Basic image analysis",
        "confidence_note": "Deterministic image metadata/statistics; not semantic scene understanding.",
        "details": details,
    }
