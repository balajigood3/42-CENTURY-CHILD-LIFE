import re

def split_text(text: str, max_chars: int = 1200) -> list[str]:
    if max_chars < 1:
        raise ValueError("max_chars must be positive.")
    cleaned = text.strip()
    if not cleaned:
        return []
    chunks, current = [], ""
    for paragraph in re.split(r"(?<=[.!?।])\s+|\n+", cleaned):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        while len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            cut = paragraph.rfind(" ", 0, max_chars + 1)
            if cut <= 0:
                cut = max_chars
            chunks.append(paragraph[:cut].strip())
            paragraph = paragraph[cut:].strip()
        candidate = f"{current} {paragraph}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks

def estimate_word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))
