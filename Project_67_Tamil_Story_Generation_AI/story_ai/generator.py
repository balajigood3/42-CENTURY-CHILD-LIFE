"""Tamil story generation with deterministic templates and optional local Ollama."""
from __future__ import annotations
import json
import urllib.request
import urllib.error

GENRE_TEMPLATES = {
    "நட்பு": "நட்பின் மதிப்பை உணர்த்தும் ஒரு கதை",
    "சாகசம்": "புதிய இடத்தில் நடக்கும் சாகசக் கதை",
    "அறிவியல்": "அறிவியல் சிந்தனையைத் தூண்டும் கதை",
    "நீதிக்கதை": "ஒரு நல்ல கருத்தை உணர்த்தும் நீதிக்கதை",
    "மர்மம்": "ஒரு புதிரைத் தீர்க்கும் மர்மக் கதை",
    "கற்பனை": "கற்பனை உலகில் நடக்கும் கதை",
}

def build_prompt(topic: str, genre: str, audience: str, length: str) -> str:
    if not topic.strip():
        raise ValueError("கதைக்கான கருப்பொருளை உள்ளிடவும்.")
    if genre not in GENRE_TEMPLATES:
        raise ValueError("தேர்ந்தெடுக்கப்பட்ட கதை வகை ஆதரிக்கப்படவில்லை.")
    if audience not in {"குழந்தைகள்", "இளைஞர்கள்", "அனைவரும்"}:
        raise ValueError("வாசகர் வகை தவறானது.")
    if length not in {"சிறியது", "நடுத்தரம்", "நீளமானது"}:
        raise ValueError("கதை நீளத் தேர்வு தவறானது.")
    size = {"சிறியது": "சுமார் 150 சொற்கள்", "நடுத்தரம்": "சுமார் 350 சொற்கள்",
            "நீளமானது": "சுமார் 650 சொற்கள்"}[length]
    return (
        "நீங்கள் தெளிவான, இயல்பான தமிழில் எழுதும் படைப்பாற்றல் மிக்க எழுத்தாளர். "
        "தமிழில் மட்டும் ஒரு முழுமையான, தனித்துவமான கதையை எழுதுங்கள். "
        f"கருப்பொருள்: {topic.strip()}. கதை வகை: {genre} ({GENRE_TEMPLATES[genre]}). "
        f"வாசகர்கள்: {audience}. நீளம்: {size}. "
        "தலைப்பு, தொடக்கம், நிகழ்வுகளின் வளர்ச்சி, நிறைவு ஆகியவை இருக்கட்டும். "
        "குழந்தைகளுக்கான கதையில் வயதுக்கேற்ற பாதுகாப்பான உள்ளடக்கம் பயன்படுத்தவும். "
        "இறுதியில் கதையின் கருத்தை ஒரு வரியில் குறிப்பிடவும்."
    )

def template_story(topic: str, genre: str, audience: str = "அனைவரும்",
                  length: str = "சிறியது") -> str:
    prompt = build_prompt(topic, genre, audience, length)
    title = topic.strip().strip(" .")
    return (
        f"## {title}\n\n"
        f"ஒரு சிறிய ஊரில் {title} என்ற எண்ணம் அனைவரின் மனதிலும் இருந்தது. "
        f"ஒருநாள், அந்த ஊரில் வாழ்ந்த சிறுவன் அருள் இதைப் பற்றி சிந்தித்தான். "
        f"அவன் தனது நண்பர்களுடன் சேர்ந்து ஒரு நல்ல முயற்சியைத் தொடங்கினான்.\n\n"
        f"முதலில் சில தடைகள் வந்தன. ஆனால் அவர்கள் ஒருவருக்கொருவர் உதவி செய்து, "
        f"ஒவ்வொரு பிரச்சினையையும் பொறுமையாகச் சமாளித்தனர். "
        f"அவர்களின் முயற்சியைக் கண்ட ஊர் மக்களும் இணைந்தனர். "
        f"சிறிய முயற்சி பெரிய மாற்றமாக வளர்ந்தது.\n\n"
        f"அன்று முதல் அந்த ஊர் மக்கள் ஒற்றுமையுடன் செயல்படத் தொடங்கினர். "
        f"அருள் மகிழ்ச்சியுடன், நல்ல எண்ணம் செயலாக மாறும்போதுதான் அதன் பயன் தெரியும் "
        f"என்று உணர்ந்தான்.\n\n**கதையின் கருத்து:** ஒற்றுமையும் விடாமுயற்சியும் நல்ல மாற்றத்தை உருவாக்கும்.\n\n"
        "_குறிப்பு: இது மாதிரி கதை. இயங்கும் உள்ளூர் LLM-ஐ இணைத்தால் கருப்பொருளுக்கேற்ற புதிய கதை உருவாகும்._"
    )

def ollama_story(prompt: str, model: str = "qwen2.5:3b",
                 host: str = "http://localhost:11434", timeout: int = 120) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        host.rstrip("/") + "/api/generate", data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollama சேவையை அணுக முடியவில்லை. Ollama இயங்குகிறதா, model pull செய்யப்பட்டுள்ளதா எனச் சரிபார்க்கவும்."
        ) from exc
    story = data.get("response", "").strip()
    if not story:
        raise RuntimeError("உள்ளூர் model காலியான பதிலை வழங்கியது.")
    return story

def generate_story(topic: str, genre: str, audience: str = "அனைவரும்",
                   length: str = "சிறியது", mode: str = "template",
                   model: str = "qwen2.5:3b", host: str = "http://localhost:11434") -> str:
    prompt = build_prompt(topic, genre, audience, length)
    if mode == "template":
        return template_story(topic, genre, audience, length)
    if mode == "ollama":
        return ollama_story(prompt, model=model, host=host)
    raise ValueError("mode must be 'template' or 'ollama'")
