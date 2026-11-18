"""Generate editable PowerPoint slides from a simple Markdown-like outline."""
from __future__ import annotations
import re
import io

MAX_SLIDES = 25
MAX_BULLETS_PER_SLIDE = 8
THEMES = {
    "Professional Blue": {
        "background": (245, 248, 253), "title": (22, 52, 94),
        "body": (45, 55, 72), "accent": (40, 105, 180),
    },
    "Modern Dark": {
        "background": (25, 31, 44), "title": (245, 247, 250),
        "body": (225, 230, 238), "accent": (90, 170, 230),
    },
    "Minimal Light": {
        "background": (255, 255, 255), "title": (35, 35, 35),
        "body": (70, 70, 70), "accent": (110, 110, 110),
    },
}

def parse_outline(outline: str, include_agenda: bool = True,
                  include_closing: bool = True) -> list[dict]:
    if not isinstance(outline, str) or not outline.strip():
        raise ValueError("Please enter a presentation outline.")
    title = "Presentation"
    slides = []
    current = None
    for raw in outline.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip() or title
        elif line.startswith("## "):
            if current:
                slides.append(current)
            current = {"title": line[3:].strip(), "bullets": []}
        elif line.startswith(("- ", "* ")):
            if current is None:
                current = {"title": "Overview", "bullets": []}
            current["bullets"].append(line[2:].strip())
        else:
            if current is None:
                current = {"title": "Overview", "bullets": []}
            current["bullets"].append(line)

    if current:
        slides.append(current)
    slides = [s for s in slides if s["title"]]
    if not slides:
        raise ValueError("Add at least one slide using a '## Slide title' heading.")
    if len(slides) > MAX_SLIDES:
        raise ValueError(f"Maximum {MAX_SLIDES} content slides are allowed.")
    for slide in slides:
        if len(slide["bullets"]) > MAX_BULLETS_PER_SLIDE:
            raise ValueError(f"Slide '{slide['title']}' has more than {MAX_BULLETS_PER_SLIDE} bullet points.")
    result = [{"title": title, "bullets": [], "kind": "title"}]
    if include_agenda:
        result.append({
            "title": "Agenda",
            "bullets": [s["title"] for s in slides[:MAX_BULLETS_PER_SLIDE]],
            "kind": "agenda",
        })
    result.extend({**s, "kind": "content"} for s in slides)
    if include_closing:
        result.append({"title": "Thank You", "bullets": ["Questions and discussion"], "kind": "closing"})
    return result

def create_presentation(slides: list[dict], author: str = "",
                        theme: str = "Professional Blue") -> bytes:
    if not slides:
        raise ValueError("At least one slide is required.")
    if theme not in THEMES:
        raise ValueError("Unknown presentation theme.")
    try:
        from pptx import Presentation
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
        from pptx.util import Inches, Pt
    except ImportError as exc:
        raise RuntimeError("Install python-pptx with: pip install python-pptx") from exc

    palette = THEMES[theme]
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    prs.core_properties.author = author
    prs.core_properties.title = slides[0]["title"] if slides else "Generated Presentation"

    for index, data in enumerate(slides):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = RGBColor(*palette["background"])

        # Accent stripe
        stripe = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.16), Inches(7.5))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = RGBColor(*palette["accent"])
        stripe.line.fill.background()

        is_title = data.get("kind") == "title"
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65 if is_title else 0.55),
                                             Inches(11.8), Inches(1.25))
        tf = title_box.text_frame
        tf.clear()
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = data["title"]
        p.font.name = "Aptos Display"
        p.font.size = Pt(34 if is_title else 30)
        p.font.bold = True
        p.font.color.rgb = RGBColor(*palette["title"])
        if is_title:
            p.alignment = PP_ALIGN.CENTER
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        else:
            p.alignment = PP_ALIGN.LEFT

        bullets = data.get("bullets", [])
        if bullets:
            body_box = slide.shapes.add_textbox(Inches(1.15), Inches(2.15 if is_title else 1.8),
                                                Inches(11.0), Inches(4.8))
            body_tf = body_box.text_frame
            body_tf.clear()
            body_tf.word_wrap = True
            for bullet_index, bullet in enumerate(bullets):
                para = body_tf.paragraphs[0] if bullet_index == 0 else body_tf.add_paragraph()
                para.text = bullet
                para.level = 0
                para.font.name = "Aptos"
                para.font.size = Pt(23 if is_title else 21)
                para.font.color.rgb = RGBColor(*palette["body"])
                para.space_after = Pt(18)
        footer = slide.shapes.add_textbox(Inches(11.4), Inches(7.05), Inches(1.2), Inches(0.25))
        fp = footer.text_frame.paragraphs[0]
        fp.text = f"{index + 1} / {len(slides)}"
        fp.font.size = Pt(10)
        fp.font.color.rgb = RGBColor(*palette["accent"])
        fp.alignment = PP_ALIGN.RIGHT

    output = io.BytesIO()
    prs.save(output)
    return output.getvalue()
