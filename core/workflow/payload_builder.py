from __future__ import annotations

from typing import Dict, Any

from ..dsl.schema import TaskModel, DSLModel


class PayloadBuilder:
    """Builds normalized payloads for activity execution."""
    @staticmethod
    def build(task: TaskModel, dsl: DSLModel) -> Dict[str, Any]:
        """
        Constructs the payload for a task execution.
        :param task:
        :param dsl:
        :return:
        """
        base_payload = task.input or {}
        return {
            "task_ref_name": task.taskReferenceName,
            **base_payload,
            "inputValues": getattr(dsl, "inputValues", None),
        }
