import json
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import requests
from .tools import SafeTools, ToolError

@dataclass
class StepLog:
    step: int
    tool: str
    arguments: dict
    status: str
    output: str
    error: str = ""

class SelfHealingAgent:
    """Bounded plan/execute/observe/repair agent with deterministic tool enforcement."""
    def __init__(self, workspace="workspace", max_attempts=2, timeout=30, use_llm=True):
        self.tools = SafeTools(workspace)
        self.max_attempts = max(1, min(int(max_attempts), 5))
        self.timeout = max(1, min(int(timeout), 120))
        self.use_llm = use_llm
        self.logs: list[StepLog] = []

    def _plan_with_ollama(self, task: str) -> list[dict] | None:
        prompt = (
            "Convert the task into a JSON array of tool calls. Allowed tools: "
            "calculator(expression), uppercase(text), word_count(text), "
            "read_file(path), write_file(path,content). Return ONLY JSON. "
            "Do not invent tools. Task: " + task
        )
        try:
            response = requests.post(
                os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/generate",
                json={"model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
                      "prompt": prompt, "stream": False, "format": "json"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            raw = response.json().get("response", "")
            data = json.loads(raw)
            if isinstance(data, dict):
                data = data.get("steps", [])
            if isinstance(data, list):
                return data
        except (requests.RequestException, ValueError, json.JSONDecodeError):
            return None
        return None

    def _fallback_plan(self, task: str) -> list[dict]:
        """Small deterministic fallback so the demo works without an LLM."""
        match = re.search(r"calculate\s+([0-9+\-*/(). %]+)", task, re.I)
        if match:
            return [{"tool": "calculator", "arguments": {"expression": match.group(1).strip()}}]
        match = re.search(r"uppercase\s*:\s*(.+)", task, re.I)
        if match:
            return [{"tool": "uppercase", "arguments": {"text": match.group(1).strip()}}]
        match = re.search(r"count words\s*:\s*(.+)", task, re.I)
        if match:
            return [{"tool": "word_count", "arguments": {"text": match.group(1).strip()}}]
        return []

    def run(self, task: str) -> dict[str, Any]:
        self.logs = []
        plan = self._plan_with_ollama(task) if self.use_llm else None
        if not plan:
            plan = self._fallback_plan(task)
        if not plan:
            return {"success": False, "message": "Could not create a supported tool plan. Try 'calculate 12 * 4'.",
                    "logs": []}
        results = []
        for index, item in enumerate(plan[:10], start=1):
            if not isinstance(item, dict):
                continue
            tool = str(item.get("tool", ""))
            args = item.get("arguments", {})
            if not isinstance(args, dict):
                args = {}
            attempt = 0
            while attempt < self.max_attempts:
                attempt += 1
                started = time.monotonic()
                try:
                    output = self.tools.call(tool, **args)
                    if time.monotonic() - started > self.timeout:
                        raise ToolError("Tool execution exceeded the configured timeout.")
                    self.logs.append(StepLog(index, tool, args, "success", str(output)))
                    results.append(str(output))
                    break
                except Exception as exc:
                    self.logs.append(StepLog(index, tool, args, "failed", "", str(exc)))
                    if attempt >= self.max_attempts:
                        return {"success": False, "message": f"Step {index} failed after {attempt} attempt(s): {exc}",
                                "results": results, "logs": [asdict(x) for x in self.logs]}
                    # Bounded repair: retry the same validated call once; no arbitrary code mutation.
            else:
                return {"success": False, "message": "Retry budget exhausted.",
                        "results": results, "logs": [asdict(x) for x in self.logs]}
        return {"success": True, "message": "Task completed.", "results": results,
                "logs": [asdict(x) for x in self.logs]}
