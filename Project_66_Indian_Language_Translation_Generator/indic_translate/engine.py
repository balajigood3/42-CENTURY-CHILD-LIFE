"""Local Indic translation using Argos Translate, with safe offline fallback."""
from __future__ import annotations

LANGUAGES = {
    "English": "en", "Tamil": "ta", "Hindi": "hi", "Telugu": "te",
    "Kannada": "kn", "Malayalam": "ml", "Bengali": "bn", "Marathi": "mr",
    "Gujarati": "gu", "Punjabi": "pa", "Urdu": "ur", "Odia": "or",
}

def validate_language(name: str) -> str:
    if name not in LANGUAGES:
        raise ValueError(f"Unsupported language: {name}")
    return LANGUAGES[name]

def offline_translate(text: str, source: str, target: str) -> str:
    if not text.strip():
        raise ValueError("Translation input cannot be empty.")
    validate_language(source)
    validate_language(target)
    if source == target:
        return text
    return (
        "Offline demo mode: translation model/package is not configured. "
        "Install an Argos Translate language package for the selected language pair. "
        "Original text: " + text
    )

def translate(text: str, source: str, target: str, use_argos: bool = False) -> str:
    if not text.strip():
        raise ValueError("Translation input cannot be empty.")
    src_code, tgt_code = validate_language(source), validate_language(target)
    if source == target:
        return text
    if not use_argos:
        return offline_translate(text, source, target)
    try:
        import argostranslate.translate
        installed = argostranslate.translate.get_installed_languages()
        from_lang = next((lang for lang in installed if lang.code == src_code), None)
        to_lang = next((lang for lang in installed if lang.code == tgt_code), None)
        if from_lang is None or to_lang is None:
            raise RuntimeError(
                f"Argos language packages missing for {source} ({src_code}) → {target} ({tgt_code}). "
                "Install the matching offline package pair first."
            )
        translation = from_lang.get_translation(to_lang)
        if translation is None:
            raise RuntimeError("No installed translation route for this language pair.")
        return translation.translate(text)
    except ImportError as exc:
        raise RuntimeError("Argos Translate is not installed. Install requirements first.") from exc
