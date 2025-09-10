from __future__ import annotations

from typing import Dict, Any

from ..dsl.schema import TaskModel, DSLModel


class PayloadBuilder:
    """Builds normalized payloads for activity execution."""
    @staticmethod
    def build(task: TaskModel) -> Dict[str, Any]:
        """
        Constructs the payload for a task execution.
        :param task:
        :return:
        """
        return {"task_ref_name":task.taskReferenceName, **task.input}
