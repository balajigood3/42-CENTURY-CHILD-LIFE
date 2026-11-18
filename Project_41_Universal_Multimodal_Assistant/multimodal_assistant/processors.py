"""Local multimodal input processors with optional offline OCR/transcription."""
from __future__ import annotations
from pathlib import Path
import mimetypes
import wave

MAX_BYTES = 15 * 1024 * 1024
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".yaml", ".yml"}

def classify_file(filename: str, content_type: str | None = None) -> str:
    ext = Path(filename).suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return "text"
    if ext == ".pdf":
        return "pdf"
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        return "image"
    if ext in {".wav", ".mp3", ".m4a", ".ogg", ".flac"}:
        return "audio"
    guessed = content_type or mimetypes.guess_type(filename)[0] or ""
    if guessed.startswith("image/"):
        return "image"
    if guessed.startswith("audio/"):
        return "audio"
    return "unsupported"

def validate_upload(filename: str, data: bytes) -> str:
    if not isinstance(data, bytes):
        raise TypeError("Uploaded content must be bytes.")
    if len(data) > MAX_BYTES:
        raise ValueError("File exceeds the 15 MB upload limit.")
    kind = classify_file(filename)
    if kind == "unsupported":
        raise ValueError("Unsupported format. Use text, PDF, image, or audio files.")
    return kind

def process_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")

def process_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(data))
        pages = []
        for i, page in enumerate(reader.pages[:30]):
            pages.append(f"[Page {i+1}]\\n{page.extract_text() or ''}")
        return "\\n\\n".join(pages).strip()
    except ImportError as exc:
        raise RuntimeError("PDF support requires pypdf. Install the project requirements.") from exc
    except Exception as exc:
        raise ValueError(f"Could not read PDF: {exc}") from exc

def process_image(data: bytes) -> dict:
    try:
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(data))
        width, height = image.size
        output = {"media_type": "image", "width": width, "height": height, "format": image.format or "unknown", "extracted_text": ""}
        try:
            import pytesseract
            output["extracted_text"] = pytesseract.image_to_string(image).strip()
            output["ocr_status"] = "completed"
        except ImportError:
            output["ocr_status"] = "unavailable"
            output["note"] = "Install pytesseract and the Tesseract OCR engine to extract text. Image pixels are not semantically interpreted."
        return output
    except ImportError as exc:
        raise RuntimeError("Image support requires Pillow.") from exc
    except Exception as exc:
        raise ValueError(f"Could not read image: {exc}") from exc

def process_audio(data: bytes, filename: str) -> dict:
    ext = Path(filename).suffix.lower()
    result = {"media_type": "audio", "filename": filename, "transcript": "", "transcription_status": "unavailable"}
    if ext == ".wav":
        import io
        try:
            with wave.open(io.BytesIO(data), "rb") as wav:
                result.update({
                    "duration_seconds": round(wav.getnframes() / float(wav.getframerate()), 2),
                    "sample_rate": wav.getframerate(),
                    "channels": wav.getnchannels(),
                })
        except Exception as exc:
            raise ValueError(f"Invalid WAV file: {exc}") from exc
    try:
        from faster_whisper import WhisperModel
        import tempfile, os
        # Small CPU model; model weights may need to be downloaded on first use.
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(data)
            temp_path = tmp.name
        try:
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, info = model.transcribe(temp_path, vad_filter=True)
            result["transcript"] = " ".join(segment.text.strip() for segment in segments).strip()
            result["language"] = info.language
            result["transcription_status"] = "completed"
        finally:
            os.unlink(temp_path)
    except ImportError:
        result["note"] = "Optional transcription requires faster-whisper and its model weights. WAV metadata is still available."
    return result

def build_response(text: str, modality: str = "text") -> dict:
    """Create a local, transparent summary of extracted content; no LLM is called."""
    clean = (text or "").strip()
    if not clean:
        summary = "No text content was extracted. Try OCR/transcription support or provide text directly."
    else:
        words = clean.split()
        summary = " ".join(words[:80])
        if len(words) > 80:
            summary += " …"
    return {
        "modality": modality,
        "character_count": len(clean),
        "word_count": len(clean.split()),
        "preview": summary,
        "processing_mode": "local_extraction_and_preview",
        "disclaimer": "This demo extracts available text and metadata; it does not provide full semantic image/audio understanding."
    }
