from __future__ import annotations

from typing import Protocol, Dict, Any

from ..dsl.schema import TaskModel, DSLModel


class TaskExecutor(Protocol):
    """Strategy for executing a task."""
    async def execute(self, task: TaskModel, dsl: DSLModel) -> Dict[str, Any]:
        """Executes the task and returns a result dictionary."""
        ...
