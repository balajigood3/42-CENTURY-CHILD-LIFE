from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

class WorkflowNode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[a-zA-Z][a-zA-Z0-9_-]{0,39}$")
    name: str = Field(min_length=2, max_length=120)
    action: str = Field(min_length=3, max_length=500)
    owner: str = Field(default="Unassigned", max_length=80)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    on_failure: str = Field(default="Stop workflow and notify owner", max_length=300)

class Workflow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=3, max_length=140)
    objective: str = Field(min_length=5, max_length=500)
    nodes: list[WorkflowNode] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def validate_graph(self):
        ids = [node.id for node in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("Node IDs must be unique")
        known = set(ids)
        for node in self.nodes:
            missing = set(node.depends_on) - known
            if missing:
                raise ValueError(f"{node.id} references unknown dependencies: {sorted(missing)}")
            if node.id in node.depends_on:
                raise ValueError(f"{node.id} cannot depend on itself")
        # Kahn's algorithm detects cycles and produces a deterministic topological order.
        indegree = {node_id: 0 for node_id in ids}
        children = {node_id: [] for node_id in ids}
        for node in self.nodes:
            for dep in node.depends_on:
                indegree[node.id] += 1
                children[dep].append(node.id)
        queue = [node_id for node_id in ids if indegree[node_id] == 0]
        visited = 0
        while queue:
            current = queue.pop(0)
            visited += 1
            for child in children[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        if visited != len(ids):
            raise ValueError("Workflow contains a dependency cycle")
        return self

    def topological_nodes(self):
        by_id = {node.id: node for node in self.nodes}
        indegree = {node.id: len(node.depends_on) for node in self.nodes}
        children = {node.id: [] for node in self.nodes}
        for node in self.nodes:
            for dep in node.depends_on:
                children[dep].append(node.id)
        queue = [node.id for node in self.nodes if indegree[node.id] == 0]
        ordered = []
        while queue:
            current = queue.pop(0)
            ordered.append(by_id[current])
            for child in children[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        return ordered
