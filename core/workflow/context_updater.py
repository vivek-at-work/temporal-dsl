from __future__ import annotations

from typing import Dict, Any

from ..dsl.schema import TaskModel


class ContextUpdater:
    """Applies an execution result back to the workflow context and model."""
    @staticmethod
    def apply(task: TaskModel, result: Dict[str, Any]) -> None:
        """Applies a result to the task's output and status."""
        task.output = result.get("output")
        task.status = result.get("status")
