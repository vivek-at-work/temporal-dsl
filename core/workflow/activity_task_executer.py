from __future__ import annotations

from datetime import timedelta
from typing import Dict, Any

from temporalio import workflow

from ..dsl.schema import TaskModel, DSLModel
from .payload_builder import PayloadBuilder

ACTIVITY_TIMEOUT_SEC = 30


class ActivityTaskExecutor:
    """Default executor that invokes an activity named '<TYPE>_TASK'."""

    def __init__(self, timeout_sec: int = ACTIVITY_TIMEOUT_SEC) -> None:
        """Initializes with activity timeout."""
        self._timeout_sec = timeout_sec

    @staticmethod
    def _activity_name(task_type_upper: str) -> str:
        """Maps a task type to activity name."""
        return f"{task_type_upper}_TASK"

    async def execute(self, task: TaskModel, dsl: DSLModel) -> Dict[str, Any]:
        """Executes the task by invoking the corresponding activity."""
        task_type = (task.type or "").upper()
        activity_name = self._activity_name(task_type)
        payload = PayloadBuilder.build(task)
        workflow.logger.info("Executing %s", activity_name)
        return await workflow.execute_activity(
            activity_name,
            payload,
            start_to_close_timeout=timedelta(seconds=self._timeout_sec),
        )
