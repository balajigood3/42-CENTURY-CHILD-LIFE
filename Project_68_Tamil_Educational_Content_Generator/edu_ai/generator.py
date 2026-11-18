"""Tamil educational content generation with local Ollama support."""
from __future__ import annotations
import json
import urllib.request
import urllib.error

SUBJECTS = ["தமிழ்", "ஆங்கிலம்", "கணிதம்", "அறிவியல்", "சமூக அறிவியல்", "கணினி அறிவியல்"]
LEVELS = ["தொடக்கநிலை", "நடுத்தரநிலை", "மேம்பட்டநிலை"]
FORMATS = ["பாடக்குறிப்பு", "எளிய விளக்கம்", "வினா-விடை", "வினாடி வினா", "பயிற்சித்தாள்"]

def build_prompt(topic: str, subject: str, level: str, content_format: str,
                 learning_objective: str = "") -> str:
    if not topic.strip():
        raise ValueError("பாடத் தலைப்பை உள்ளிடவும்.")
    if subject not in SUBJECTS:
        raise ValueError("பாடப்பிரிவு சரியானதல்ல.")
    if level not in LEVELS:
        raise ValueError("கற்றல் நிலை சரியானதல்ல.")
    if content_format not in FORMATS:
        raise ValueError("உள்ளடக்க வடிவம் சரியானதல்ல.")
    objective = learning_objective.strip() or "மாணவர் தலைப்பின் அடிப்படைக் கருத்தைப் புரிந்துகொள்ளுதல்"
    return (
        "நீங்கள் அனுபவமிக்க தமிழ் ஆசிரியர். கீழ்கண்ட விவரங்களுக்கேற்ப துல்லியமான, "
        "வயதுக்கும் கற்றல் நிலைக்கும் ஏற்ற கல்வி உள்ளடக்கத்தை தமிழில் உருவாக்குங்கள்.\n"
        f"பாடப்பிரிவு: {subject}\nதலைப்பு: {topic.strip()}\n"
        f"கற்றல் நிலை: {level}\nவடிவம்: {content_format}\n"
        f"கற்றல் நோக்கம்: {objective}\n"
        "தெளிவான தலைப்புகள், எடுத்துக்காட்டுகள், படிப்படியான விளக்கம் பயன்படுத்தவும். "
        "தெரியாத தகவல்களை உண்மையாகக் கூற வேண்டாம். வினாக்கள் இருந்தால் விடைகளையும் "
        "சேர்க்கவும். இறுதியில் 3 முக்கிய கருத்துகளைச் சுருக்கமாகக் கொடுக்கவும்."
    )

def sample_content(topic: str, subject: str, level: str, content_format: str) -> str:
    if not topic.strip():
        raise ValueError("பாடத் தலைப்பை உள்ளிடவும்.")
    build_prompt(topic, subject, level, content_format)
    if content_format == "வினா-விடை":
        body = (
            f"1. {topic} என்றால் என்ன?\n"
            f"   விடை: {topic} என்பது இந்தப் பாடத்தில் கற்கப்படும் முக்கிய கருத்தாகும்.\n"
            f"2. {topic} ஏன் முக்கியம்?\n"
            "   விடை: அதன் பயன்பாடு மற்றும் அடிப்படைக் கருத்துகளைப் புரிந்துகொள்ள உதவுகிறது.\n"
        )
    elif content_format == "வினாடி வினா":
        body = (
            f"1. {topic} எந்தப் பாடப்பிரிவுடன் தொடர்புடையது?\n"
            f"   A) {subject}  B) இசை  C) விளையாட்டு\n"
            "   சரியான விடை: A\n"
            f"2. {topic} கற்கும் போது முதலில் செய்ய வேண்டியது?\n"
            "   A) மனப்பாடம் மட்டும்  B) கருத்தைப் புரிந்துகொள்  C) தவிர்த்துவிடு\n"
            "   சரியான விடை: B\n"
        )
    elif content_format == "பயிற்சித்தாள்":
        body = (
            f"1. {topic} பற்றி இரண்டு வரிகளில் எழுதுக.\n"
            f"2. {topic} தொடர்பான ஓர் எடுத்துக்காட்டைக் கொடுக்கவும்.\n"
            f"3. {topic} ஏன் பயன்படுகிறது என்பதை விளக்குக.\n"
            "சுயமதிப்பீடு: உங்கள் பதில்களை பாடக்குறிப்புடன் ஒப்பிட்டுப் பார்க்கவும்.\n"
        )
    else:
        body = (
            f"**அறிமுகம்:** {topic} என்பது {subject} பாடத்தில் கற்க வேண்டிய ஒரு தலைப்பு.\n\n"
            f"**எளிய விளக்கம்:** {topic} பற்றிய அடிப்படைக் கருத்துகளை முதலில் புரிந்துகொள்ளுங்கள். "
            "பின்னர் அதன் கூறுகள், பண்புகள் மற்றும் பயன்பாடுகளை எடுத்துக்காட்டுகளுடன் கற்கலாம்.\n\n"
            "**கற்றல் படிகள்:**\n"
            "1. தலைப்பின் முக்கிய சொற்களை அறிந்துகொள்ளுங்கள்.\n"
            "2. ஒவ்வொரு கருத்தையும் தனித்தனியாகப் படியுங்கள்.\n"
            "3. எடுத்துக்காட்டுகளைப் பயிற்சி செய்யுங்கள்.\n"
            "4. உங்கள் புரிதலை வினாக்கள் மூலம் சரிபாருங்கள்.\n\n"
            f"**எடுத்துக்காட்டு:** {topic} தொடர்பான ஒரு அன்றாட வாழ்க்கைச் சூழலைக் கண்டறிந்து விளக்குங்கள்.\n"
        )
    return (
        f"# {topic}\n\n"
        f"- **பாடப்பிரிவு:** {subject}\n- **நிலை:** {level}\n- **வடிவம்:** {content_format}\n\n"
        f"{body}\n**முக்கிய கருத்துகள்:**\n- தலைப்பின் அடிப்படை வரையறையைப் புரிந்துகொள்ளுங்கள்.\n"
        "- எடுத்துக்காட்டுகளுடன் கற்றலை உறுதிப்படுத்துங்கள்.\n"
        "- பயிற்சி செய்து உங்கள் புரிதலை மதிப்பிடுங்கள்.\n\n"
        "_இது மாதிரி உள்ளடக்கம். பாடநூல் அல்லது ஆசிரியர் வழிகாட்டுதலுடன் சரிபார்க்கவும்._"
    )

def ollama_generate(prompt: str, model: str = "qwen2.5:3b",
                    host: str = "http://localhost:11434", timeout: int = 120) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        host.rstrip("/") + "/api/generate", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError("Ollama சேவையை அணுக முடியவில்லை. Ollama இயங்குகிறதா எனச் சரிபார்க்கவும்.") from exc
    output = data.get("response", "").strip()
    if not output:
        raise RuntimeError("உள்ளூர் model காலியான பதிலை வழங்கியது.")
    return output

def generate_content(topic: str, subject: str, level: str,
                     content_format: str, learning_objective: str = "",
                     mode: str = "sample", model: str = "qwen2.5:3b") -> str:
    prompt = build_prompt(topic, subject, level, content_format, learning_objective)
    if mode == "sample":
        return sample_content(topic, subject, level, content_format)
    if mode == "ollama":
        return ollama_generate(prompt, model=model)
    raise ValueError("mode must be 'sample' or 'ollama'")
