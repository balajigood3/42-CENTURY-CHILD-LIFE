import io
import pytest
from presentation_builder import parse_outline, create_presentation

SAMPLE = """# Demo deck
## Problem
- Users wait too long
- Manual work is repetitive
## Solution
- Automate the workflow
- Measure improvements
"""

def test_parse_outline_with_agenda_and_closing():
    slides = parse_outline(SAMPLE)
    assert slides[0]["title"] == "Demo deck"
    assert slides[1]["title"] == "Agenda"
    assert slides[-1]["kind"] == "closing"
    assert len(slides) == 5

def test_parse_outline_without_optional_slides():
    slides = parse_outline(SAMPLE, include_agenda=False, include_closing=False)
    assert len(slides) == 3

def test_rejects_empty_outline():
    with pytest.raises(ValueError):
        parse_outline("  ")

def test_rejects_too_many_content_slides():
    outline = "\n".join(f"## Slide {i}" for i in range(26))
    with pytest.raises(ValueError):
        parse_outline(outline)

def test_rejects_too_many_bullets():
    outline = "## Slide\n" + "\n".join(f"- Point {i}" for i in range(9))
    with pytest.raises(ValueError):
        parse_outline(outline)

def test_generates_editable_pptx():
    slides = parse_outline(SAMPLE)
    data = create_presentation(slides, author="Unit Test")
    assert data[:2] == b"PK"
    from pptx import Presentation
    prs = Presentation(io.BytesIO(data))
    assert len(prs.slides) == len(slides)
    assert prs.slides[0].shapes.title is None  # custom editable text boxes
    texts = [shape.text for slide in prs.slides for shape in slide.shapes if shape.has_text_frame]
    assert "Demo deck" in texts
    assert any("Automate the workflow" in text for text in texts)

def test_rejects_unknown_theme():
    with pytest.raises(ValueError):
        create_presentation([{"title": "Test", "bullets": []}], theme="Neon")
