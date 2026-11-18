import requests

class SelfReflectionEngine:
    def __init__(self,model="qwen2.5:3b",base_url="http://localhost:11434",timeout=180):
        self.model=model; self.base_url=base_url.rstrip("/"); self.timeout=timeout

    def _generate(self,prompt,temperature=0.2):
        r=requests.post(f"{self.base_url}/api/generate",
            json={"model":self.model,"prompt":prompt,"stream":False,
                  "options":{"temperature":temperature}},timeout=self.timeout)
        r.raise_for_status()
        answer=r.json().get("response","").strip()
        if not answer: raise RuntimeError("Ollama returned an empty response")
        return answer

    def run(self,task,rounds=2):
        draft=self._generate(
            "Complete this task accurately. Be explicit about uncertainty and do not invent facts.\n"
            f"TASK:\n{task}\n\nINITIAL ANSWER:"
        )
        reflections=[]
        for index in range(max(1,min(int(rounds),3))):
            critique=self._generate(
                "Review the draft for correctness, relevance, missing steps, unsupported claims, "
                "clarity, and ambiguity. Identify concrete improvements. If evidence is insufficient, say so.\n"
                f"TASK:\n{task}\nDRAFT:\n{draft}\n\nCRITIQUE:"
            )
            revision=self._generate(
                "Improve the draft using the critique. Correct errors, remove unsupported certainty, "
                "and preserve useful content. Do not mention hidden reasoning. Provide only the improved answer.\n"
                f"TASK:\n{task}\nDRAFT:\n{draft}\nCRITIQUE:\n{critique}\n\nREVISED ANSWER:"
            )
            reflections.append({"critique":critique,"revision":revision})
            draft=revision
        return {"final_answer":draft,"reflections":reflections}
