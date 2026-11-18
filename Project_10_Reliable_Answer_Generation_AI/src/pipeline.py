import requests
from src.validators import basic_checks

class ReliableAnswerPipeline:
    def __init__(self,model="qwen2.5:3b",base_url="http://localhost:11434",timeout=180):
        self.model=model; self.base_url=base_url.rstrip("/"); self.timeout=timeout

    def _generate(self,prompt,temperature=0.1):
        r=requests.post(f"{self.base_url}/api/generate",
            json={"model":self.model,"prompt":prompt,"stream":False,
                  "options":{"temperature":temperature}},timeout=self.timeout)
        r.raise_for_status()
        answer=r.json().get("response","").strip()
        if not answer: raise RuntimeError("Empty model response")
        return answer

    def run(self,question,evidence=""):
        evidence=evidence.strip()
        evidence_block=evidence if evidence else "No external evidence was provided."
        draft=self._generate(f"""Answer the question carefully.
Use only the supplied evidence for claims that require factual support.
If evidence is missing, clearly say what cannot be verified. Never fabricate citations.
Separate evidence-backed facts from general explanation.
EVIDENCE:
{evidence_block}
QUESTION:
{question}
DRAFT ANSWER:""")
        checks=basic_checks(question,draft,evidence)
        review=self._generate(f"""Audit this answer for unsupported factual claims, contradictions with evidence,
missing caveats, and whether it actually answers the question.
Do not assume the draft is correct. If no evidence was supplied, explicitly note that factual claims cannot be verified.
Return a concise audit with sections: Supported, Unverified, Problems, Suggested correction.
QUESTION: {question}
EVIDENCE: {evidence_block}
DRAFT: {draft}
AUDIT:""")
        final=self._generate(f"""Revise the answer using the audit and deterministic checks.
Do not add unsupported facts. Clearly label uncertainty and say "Insufficient evidence to verify" when needed.
Do not invent sources, citations, numbers, or quotations.
QUESTION: {question}
EVIDENCE: {evidence_block}
DRAFT: {draft}
AUDIT: {review}
DETERMINISTIC CHECKS: {checks}
FINAL ANSWER:""")
        status="Evidence supplied — reviewed" if evidence else "No evidence supplied — uncertainty required"
        return {"draft":draft,"verification":review+"\n\nDeterministic checks: "+str(checks),
                "final_answer":final,"status":status}
