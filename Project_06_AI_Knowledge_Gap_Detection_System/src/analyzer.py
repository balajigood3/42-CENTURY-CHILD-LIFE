import json
import re
import requests

PROMPT = """You are a rigorous knowledge-gap analyst.
Analyze only the supplied text against the stated goal. A knowledge gap is important information that is absent, underspecified, unsupported, or needed to make a decision.
Do not invent facts. Distinguish an explicit absence from information that may simply be outside the supplied excerpt.
Return ONLY valid JSON:
{
 "summary": "brief overall assessment",
 "strengths": ["information clearly covered in the text"],
 "gaps": [
  {"topic":"topic", "missing_information":"specific missing or unclear information",
   "why_it_matters":"impact of the gap", "question_to_resolve":"one answerable question",
   "evidence_needed":"document, metric, source, test, or evidence needed",
   "priority":"high|medium|low"}
 ]
}
Use an empty gaps list if no material gaps are apparent. Prioritize decision-critical gaps. Keep findings concise."""

class KnowledgeGapAnalyzer:
    def __init__(self, model="qwen2.5:3b", base_url="http://localhost:11434", timeout=150):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def analyze(self, text, goal=""):
        prompt = f"{PROMPT}\n\nGOAL: {goal or 'General completeness review'}\n\nTEXT:\n{text}"
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False,
                      "format": "json", "options": {"temperature": 0.1}},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            parsed = self._parse(payload.get("response", ""))
            return self._normalize(parsed)
        except (requests.RequestException, ValueError, TypeError, json.JSONDecodeError):
            return self._fallback(text, goal)

    @staticmethod
    def _parse(raw):
        raw = raw.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.S)
            if not match:
                raise ValueError("Model did not return JSON")
            return json.loads(match.group(0))

    @staticmethod
    def _normalize(data):
        if not isinstance(data, dict):
            raise ValueError("Invalid model result")
        gaps = data.get("gaps", [])
        strengths = data.get("strengths", [])
        if not isinstance(gaps, list) or not isinstance(strengths, list):
            raise ValueError("Invalid result schema")
        clean_gaps = []
        for gap in gaps:
            if not isinstance(gap, dict):
                continue
            priority = str(gap.get("priority", "medium")).lower()
            if priority not in {"high", "medium", "low"}:
                priority = "medium"
            clean_gaps.append({
                "topic": str(gap.get("topic", "Unspecified")),
                "missing_information": str(gap.get("missing_information", "")),
                "why_it_matters": str(gap.get("why_it_matters", "")),
                "question_to_resolve": str(gap.get("question_to_resolve", "")),
                "evidence_needed": str(gap.get("evidence_needed", "")),
                "priority": priority,
            })
        return {
            "summary": str(data.get("summary", "Analysis completed.")),
            "strengths": [str(x) for x in strengths if isinstance(x, (str, int, float))],
            "gaps": clean_gaps,
        }

    @staticmethod
    def _fallback(text, goal):
        # Transparent heuristic fallback: flags common underspecified areas, not semantic proof.
        lowered = text.lower()
        candidates = [
            (["security", "secure", "பாதுகாப்பு"], "Security controls",
             "பாதுகாப்பு நடவடிக்கைகள், அணுகல் கட்டுப்பாடு அல்லது தரவு கையாளல் விவரங்கள் தெளிவாக இல்லை."),
            (["performance", "latency", "throughput", "செயல்திறன்"], "Performance",
             "செயல்திறன் அளவுகோல்கள் அல்லது சுமைச் சோதனை விவரங்கள் குறிப்பிடப்படவில்லை."),
            (["cost", "budget", "செலவு"], "Cost and budget",
             "செலவு மதிப்பீடு, செலவுக் கூறுகள் அல்லது பட்ஜெட் வரம்பு தெளிவாக இல்லை."),
            (["test", "testing", "சோதனை"], "Testing and validation",
             "சோதனைத் திட்டம், ஏற்றுக்கொள்ளும் அளவுகோல்கள் அல்லது முடிவுகள் குறிப்பிடப்படவில்லை."),
            (["owner", "responsible", "பொறுப்பு"], "Ownership",
             "பொறுப்பாளர் அல்லது முடிவு எடுக்கும் உரிமையாளர் தெளிவாக இல்லை."),
        ]
        gaps = []
        for keywords, topic, missing in candidates:
            if not any(k in lowered for k in keywords):
                gaps.append({
                    "topic": topic, "missing_information": missing,
                    "why_it_matters": "இந்த விவரம் இல்லாமல் முழுமை மற்றும் நடைமுறை சாத்தியத்தை மதிப்பிடுவது கடினம்.",
                    "question_to_resolve": f"{topic} தொடர்பான திட்டவட்டமான விவரங்கள் என்ன?",
                    "evidence_needed": "ஆவணம், அளவீடு, சோதனை முடிவு அல்லது பொறுப்பாளர் உறுதிப்படுத்தல்.",
                    "priority": "medium",
                })
        return {
            "summary": "Ollama-ஐ அணுக முடியாததால் எளிய keyword heuristic பயன்படுத்தப்பட்டது. இது semantic analysis அல்ல.",
            "strengths": ["உள்ளீட்டு உரை ஆய்வுக்காகப் பெறப்பட்டது."],
            "gaps": gaps[:5],
        }
