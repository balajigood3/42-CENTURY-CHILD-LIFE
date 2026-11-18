from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Task(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^T[0-9]{2}$")
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=5, max_length=400)
    milestone: str = Field(min_length=2, max_length=80)
    priority: str = Field(pattern=r"^(High|Medium|Low)$")
    estimated_days: int = Field(ge=1, le=365)
    depends_on: list[str] = Field(default_factory=list)
    success_criteria: str = Field(min_length=3, max_length=250)

class GoalPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goal: str = Field(min_length=5, max_length=300)
    deadline_days: int = Field(ge=1, le=3650)
    assumptions: list[str] = Field(default_factory=list)
    milestones: list[str] = Field(min_length=1, max_length=12)
    tasks: list[Task] = Field(min_length=1, max_length=40)

    @model_validator(mode="after")
    def validate_dependencies(self):
        ids = [t.id for t in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("Task IDs must be unique")
        known = set(ids)
        for task in self.tasks:
            missing = set(task.depends_on) - known
            if missing:
                raise ValueError(f"{task.id} has unknown dependencies: {sorted(missing)}")
            if task.id in task.depends_on:
                raise ValueError(f"{task.id} cannot depend on itself")
        indegree = {task_id: 0 for task_id in ids}
        children = {task_id: [] for task_id in ids}
        for task in self.tasks:
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
            raise ValueError("Task dependencies contain a cycle")
        if len(set(self.milestones)) != len(self.milestones):
            raise ValueError("Milestone names must be unique")
        return self

    def ordered_tasks(self):
        by_id = {task.id: task for task in self.tasks}
        indegree = {task.id: len(task.depends_on) for task in self.tasks}
        children = {task.id: [] for task in self.tasks}
        for task in self.tasks:
            for dep in task.depends_on:
                children[dep].append(task.id)
        queue = [task.id for task in self.tasks if indegree[task.id] == 0]
        result = []
        while queue:
            current = queue.pop(0)
            result.append(by_id[current])
            for child in children[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        return result
