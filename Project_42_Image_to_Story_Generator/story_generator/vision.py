"""Image understanding adapters: optional local BLIP model, safe metadata/OCR fallback."""
from __future__ import annotations
from io import BytesIO
from PIL import Image
import os

MAX_IMAGE_BYTES = 12 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

def validate_image(data: bytes) -> Image.Image:
    if not isinstance(data, bytes):
        raise TypeError("Image content must be bytes.")
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Image is empty or exceeds the 12 MB limit.")
    try:
        probe = Image.open(BytesIO(data))
        original_format = probe.format
        probe.verify()
        if original_format not in ALLOWED_FORMATS:
            raise ValueError("Only JPEG, PNG, and WEBP images are supported.")
        image = Image.open(BytesIO(data)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Invalid image: {exc}") from exc
    if image.format not in ALLOWED_FORMATS and image.format is not None:
        raise ValueError("Only JPEG, PNG, and WEBP images are supported.")
    if image.width * image.height > 20_000_000:
        raise ValueError("Image dimensions exceed the 20-megapixel limit.")
    return image

def describe_image(data: bytes, use_blip: bool = False) -> dict:
    image = validate_image(data)
    result = {
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "caption": "",
        "caption_source": "metadata_fallback",
        "ocr_text": "",
        "note": "",
    }
    if use_blip:
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            import torch
            model_name = os.getenv("BLIP_MODEL", "Salesforce/blip-image-captioning-base")
            processor = BlipProcessor.from_pretrained(model_name)
            model = BlipForConditionalGeneration.from_pretrained(model_name)
            inputs = processor(image, return_tensors="pt")
            with torch.no_grad():
                output = model.generate(**inputs, max_new_tokens=60)
            result["caption"] = processor.decode(output[0], skip_special_tokens=True)
            result["caption_source"] = "local_blip_model"
        except ImportError:
            result["note"] = "BLIP support requires optional transformers and torch packages."
        except Exception as exc:
            result["note"] = f"BLIP captioning unavailable: {exc}"
    if not result["caption"]:
        try:
            import pytesseract
            result["ocr_text"] = pytesseract.image_to_string(image).strip()
        except ImportError:
            result["note"] = result["note"] or "Install pytesseract and the Tesseract binary for optional OCR."
        result["caption"] = (
            f"An image with dimensions {image.width} by {image.height} pixels"
            + (f" containing visible text: {result['ocr_text'][:240]}" if result["ocr_text"] else ".")
        )
    return result
