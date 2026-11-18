"""Local-first multimodal input processing and transparent response assembly."""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageStat
import io
import re

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}

def validate_upload(filename: str, size: int, modality: str) -> None:
    extensions = IMAGE_EXTENSIONS if modality == "image" else AUDIO_EXTENSIONS if modality == "audio" else set()
    if not extensions:
        raise ValueError("Modality must be image or audio.")
    if Path(filename).suffix.lower() not in extensions:
        raise ValueError(f"Unsupported {modality} format.")
    if size <= 0:
        raise ValueError("Uploaded file is empty.")
    if size > MAX_UPLOAD_BYTES:
        raise ValueError("Each upload must be 20 MB or smaller.")

def image_context(image: Image.Image, use_blip: bool = False) -> str:
    if image is None:
        raise ValueError("An image is required.")
    width, height = image.size
    if width * height > 25_000_000:
        raise ValueError("Image dimensions exceed the 25 megapixel safety limit.")
    if use_blip:
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError(
                "BLIP is optional. Install it with: pip install transformers torch"
            ) from exc
        global _BLIP_PIPE
        try:
            pipe = _BLIP_PIPE
        except NameError:
            _BLIP_PIPE = pipeline(
                "image-to-text",
                model="Salesforce/blip-image-captioning-base",
                device=-1,
            )
            pipe = _BLIP_PIPE
        captions = pipe(image.convert("RGB"))
        caption = captions[0].get("generated_text", "") if captions else ""
        return f"Image dimensions: {width}x{height}. Model caption: {caption}".strip()
    stats = ImageStat.Stat(image.convert("RGB").resize((min(width, 128), min(height, 128))))
    avg = [round(channel, 1) for channel in stats.mean]
    return f"Image dimensions: {width}x{height}; average RGB values: {avg}. Semantic image analysis is disabled."

def transcribe_audio(audio_bytes: bytes, filename: str, model_size: str = "tiny") -> str:
    validate_upload(filename, len(audio_bytes), "audio")
    if model_size not in {"tiny", "base", "small"}:
        raise ValueError("Whisper model size must be tiny, base, or small.")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Whisper is optional. Install it with: pip install faster-whisper"
        ) from exc
    temp_path = None
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            temp_path = tmp.name
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(temp_path, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        raise RuntimeError(f"Audio transcription failed: {exc}") from exc
    finally:
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()

def build_response(question: str, contexts: list[tuple[str, str]]) -> dict:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a question.")
    normalized = []
    for modality, content in contexts:
        content = str(content).strip()
        if content:
            normalized.append({"modality": str(modality), "content": content})
    if not normalized:
        raise ValueError("Provide at least one non-empty context item.")
    sections = [f"### {item['modality']}\n{item['content']}" for item in normalized]
    combined = "\n\n".join(sections)
    response = (
        "I have combined the available inputs below. This starter version does not "
        "perform open-ended reasoning; use the context as evidence and verify the details.\n\n"
        + combined
    )
    markdown = f"# Multimodal Assistant Response\n\n**Question:** {question.strip()}\n\n{response}\n"
    return {
        "question": question.strip(),
        "response": response,
        "context": normalized,
        "markdown": markdown,
        "mode_note": "Local context aggregation. Optional BLIP/Whisper models provide image captions and audio transcripts.",
    }
