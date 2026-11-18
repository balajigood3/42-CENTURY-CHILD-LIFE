"""Template-driven story generation from an image caption; no paid API required."""
from __future__ import annotations
import random

STYLES = {
    "adventure": {
        "opening": "The moment began quietly, but {scene} held the promise of an adventure.",
        "middle": "A curious discovery changed the direction of the day. Instead of turning back, the unlikely hero chose to explore, learning that courage often begins with one small step.",
        "ending": "By sunset, the journey had become a story worth remembering—and a reminder that wonder is often hiding in ordinary places."
    },
    "fairy_tale": {
        "opening": "Once upon a time, in a place suggested by {scene}, a small mystery waited to be solved.",
        "middle": "A kind-hearted traveler followed a trail of clues and met someone who needed help. Through patience and generosity, the mystery slowly unfolded.",
        "ending": "From that day forward, the place was remembered not for its mystery, but for the kindness that transformed it."
    },
    "science_fiction": {
        "opening": "In the near future, {scene} became the setting for an unexpected signal.",
        "middle": "The signal carried a message from beyond the familiar world. The crew examined the evidence, questioned their assumptions, and discovered a new possibility for humanity.",
        "ending": "The mission ended with more questions than answers, but one certainty remained: exploration had only just begun."
    },
    "mystery": {
        "opening": "At first glance, {scene} seemed ordinary. Then one detail refused to make sense.",
        "middle": "The investigator gathered clues, compared every possibility, and noticed a pattern everyone else had overlooked. The truth was closer than anyone expected.",
        "ending": "When the final clue fell into place, the mystery was solved—and the ordinary scene was never seen in quite the same way again."
    }
}

def generate_story(caption: str, style: str = "adventure", user_prompt: str = "", max_words: int = 220) -> dict:
    if not isinstance(caption, str) or not caption.strip():
        raise ValueError("A non-empty image description is required.")
    if style not in STYLES:
        raise ValueError(f"Unsupported style: {style}")
    if not isinstance(max_words, int) or not 60 <= max_words <= 500:
        raise ValueError("max_words must be between 60 and 500.")
    scene = caption.strip().replace("\n", " ")[:300]
    parts = STYLES[style]
    title = f"The Secret of {scene[:36].strip().title()}"
    prompt_line = f"Story direction: {user_prompt.strip()[:180]}. " if user_prompt.strip() else ""
    story = " ".join([
        parts["opening"].format(scene=scene),
        prompt_line + parts["middle"],
        parts["ending"]
    ])
    words = story.split()
    if len(words) > max_words:
        story = " ".join(words[:max_words])
    return {
        "title": title,
        "style": style,
        "image_description": scene,
        "story": story,
        "word_count": len(story.split()),
        "generation_method": "local_template_based",
        "disclaimer": "The story is generated from the supplied caption/description. A fallback caption may contain only image metadata or OCR text."
    }
