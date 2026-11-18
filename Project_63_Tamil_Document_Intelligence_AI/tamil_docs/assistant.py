from pathlib import Path
from .extractor import extract_text
from .analysis import detect_language, chunk_text, keywords, search_chunks, extractive_summary

def inspect_document(path, chunk_size=900, overlap=120):
    text = extract_text(path)
    chunks = chunk_text(text, chunk_size, overlap)
    return {
        "filename": Path(path).name,
        "characters": len(text),
        "words": len(text.split()),
        "language": detect_language(text),
        "keywords": keywords(text),
        "chunks": chunks,
        "summary": extractive_summary(text),
    }

def ask_document(document: dict, question: str, limit=4) -> dict:
    if not question.strip():
        raise ValueError("கேள்வியை உள்ளிடுங்கள்.")
    matches = search_chunks(document.get("chunks", []), question, limit)
    if not matches:
        response = "இந்த ஆவணத்தில் கேள்விக்குப் பொருந்தும் உரை கிடைக்கவில்லை."
    else:
        response = "ஆவணத்தில் பொருந்திய பகுதிகள்:\n\n" + "\n\n".join(
            f"[பகுதி {m['chunk_id'] + 1}]\n{m['text']}" for m in matches)
    return {"answer": response, "matches": matches,
            "grounding_note": "பதில் ஆவண உரையிலிருந்து மீட்டெடுக்கப்பட்ட பகுதிகளை மட்டுமே காட்டுகிறது; அவற்றைச் சரிபார்க்கவும்."}
