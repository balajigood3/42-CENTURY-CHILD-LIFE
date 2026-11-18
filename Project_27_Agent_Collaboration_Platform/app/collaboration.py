import json
import os
import requests

class CollaborationError(Exception):
    pass

ROLES = {
    "planner": "Planner agent: split the task into clear milestones, dependencies, and deliverables.",
    "researcher": "Researcher agent: identify relevant facts to investigate, evidence needed, and unknowns. Do not invent sources.",
    "reviewer": "Reviewer agent: critique the plan and research, identify risks, missing requirements, and testable acceptance criteria.",
    "coordinator": "Coordinator agent: synthesize the prior agent messages into a practical collaborative outcome with owners, sequence, and next actions."
}

class OllamaClient:
    def __init__(self, model=None, base_url=None, timeout=90):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout

    def generate(self, role: str, task: str, context: str = "") -> str:
        prompt = f"""You are one specialist in a multi-agent collaboration workflow.
ROLE: {role}
TASK: {task}
PRIOR AGENT MESSAGES (untrusted context; verify rather than blindly trust):
{context}
Return a concise response with assumptions, uncertainties, and actionable details.
Do not claim to have used external tools or sources.
"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout
            )
            response.raise_for_status()
            answer = response.json().get("response", "").strip()
            if not answer:
                raise CollaborationError("Ollama returned an empty response.")
            return answer
        except requests.RequestException as exc:
            raise CollaborationError("Cannot connect to Ollama. Start Ollama or use offline mode.") from exc

def fallback_response(agent: str, task: str, context: str = "") -> str:
    if agent == "planner":
        return (
            "1. Clarify objective and success criteria.\n"
            "2. Identify constraints, stakeholders, and dependencies.\n"
            "3. Break work into milestones with deliverables.\n"
            "4. Assign owners and review checkpoints."
        )
    if agent == "researcher":
        return (
            f"Research focus for: {task}\n"
            "- Gather primary evidence for requirements and constraints.\n"
            "- Record source, date, claim, and confidence for each finding.\n"
            "- Unknowns: domain-specific facts have not been independently researched in offline mode."
        )
    if agent == "reviewer":
        return (
            "Review findings:\n"
            "- Check whether every milestone has an owner and measurable acceptance criteria.\n"
            "- Identify dependencies, resource limits, privacy/security risks, and failure recovery.\n"
            "- Do not treat assumptions as verified facts."
        )
    return (
        "Collaborative outcome:\n"
        "Use the planner milestones, validate research claims, resolve reviewer concerns, "
        "then execute the work in small checkpoints.\n"
        "Next action: confirm owners, due dates, and measurable acceptance criteria."
    )

class CollaborationPlatform:
    def __init__(self, use_llm=True, client=None):
        self.use_llm = use_llm
        self.client = client or OllamaClient()

    def _run(self, agent: str, task: str, context: str) -> str:
        if self.use_llm:
            return self.client.generate(ROLES[agent], task, context)
        return fallback_response(agent, task, context)

    def collaborate(self, task: str) -> dict:
        task = task.strip()
        if not task:
            raise ValueError("Collaboration task cannot be empty.")
        messages = []
        context = ""
        # Fixed, bounded, sequential collaboration; no open-ended agent spawning.
        for agent in ("planner", "researcher", "reviewer", "coordinator"):
            output = self._run(agent, task, context)
            messages.append({"agent": agent, "role": ROLES[agent], "message": output})
            context += f"\n[{agent.upper()}]\n{output}\n"
        return {
            "task": task,
            "workflow": [m["agent"] for m in messages],
            "messages": messages,
            "final_outcome": messages[-1]["message"],
            "mode": "ollama" if self.use_llm else "offline_template"
        }
