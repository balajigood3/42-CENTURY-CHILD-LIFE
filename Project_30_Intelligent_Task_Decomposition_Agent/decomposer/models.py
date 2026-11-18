from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Subtask(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^S[0-9]{2,3}$")
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=5, max_length=400)
    parent_id: str | None = None
    priority: str = Field(pattern=r"^(Critical|High|Medium|Low)$")
    estimated_hours: float = Field(gt=0, le=1000)
    depends_on: list[str] = Field(default_factory=list)
    deliverable: str = Field(min_length=3, max_length=250)
    acceptance_criteria: str = Field(min_length=3, max_length=300)

class TaskBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project: str = Field(min_length=3, max_length=160)
    objective: str = Field(min_length=5, max_length=500)
    assumptions: list[str] = Field(default_factory=list)
    subtasks: list[Subtask] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_hierarchy_and_dependencies(self):
        ids = [task.id for task in self.subtasks]
        if len(ids) != len(set(ids)):
            raise ValueError("Subtask IDs must be unique")
        known = set(ids)
        for task in self.subtasks:
            if task.parent_id is not None and task.parent_id not in known:
                raise ValueError(f"{task.id} references unknown parent {task.parent_id}")
            if task.parent_id == task.id:
                raise ValueError(f"{task.id} cannot be its own parent")
            missing = set(task.depends_on) - known
            if missing:
                raise ValueError(f"{task.id} references unknown dependencies: {sorted(missing)}")
            if task.id in task.depends_on:
                raise ValueError(f"{task.id} cannot depend on itself")
        # Parent hierarchy must be acyclic.
        for task in self.subtasks:
            seen, current = set(), task
            while current.parent_id is not None:
                if current.id in seen:
                    raise ValueError("Parent hierarchy contains a cycle")
                seen.add(current.id)
                current = next(t for t in self.subtasks if t.id == current.parent_id)
        # Dependency DAG validation.
        indegree = {task_id: 0 for task_id in ids}
        children = {task_id: [] for task_id in ids}
        for task in self.subtasks:
            for dep in task.depends_on:
                indegree[task.id] += 1
                children[dep].append(task.id)
        queue = [task_id for task_id in ids if indegree[task_id] == 0]
        visited = 0
        while queue:
            current = queue.pop(0)
            visited += 1
            for child in children[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        if visited != len(ids):
            raise ValueError("Subtask dependencies contain a cycle")
        return self

    def execution_order(self):
        by_id = {t.id: t for t in self.subtasks}
        indegree = {t.id: len(t.depends_on) for t in self.subtasks}
        children = {t.id: [] for t in self.subtasks}
        for task in self.subtasks:
            for dep in task.depends_on:
                children[dep].append(task.id)
        queue = [t.id for t in self.subtasks if indegree[t.id] == 0]
        result = []
        while queue:
            current = queue.pop(0)
            result.append(by_id[current])
            for child in children[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        return result

    @property
    def total_estimated_hours(self):
        return round(sum(t.estimated_hours for t in self.subtasks), 2)
