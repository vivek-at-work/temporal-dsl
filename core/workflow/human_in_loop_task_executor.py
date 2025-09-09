from __future__ import annotations

from typing import Dict, Any

from temporalio import workflow

from ..dsl.schema import TaskModel, DSLModel
from .human_in_loop_signal_state import HumanInLoopSignalState


class HumanInLoopTaskExecutor:
    """Executor for APPROVAL tasks that blocks on a signal."""
    def __init__(self, state: HumanInLoopSignalState) -> None:
        self._state = state

    async def execute(self, task: TaskModel, dsl: DSLModel) -> Dict[str, Any]:
        """Waits for an approval signal to proceed."""
        workflow.logger.info("[APPROVAL] Waiting for approval on '%s'", task.taskReferenceName)
        await self._state.wait()
        return {
            "task_ref_name": task.taskReferenceName,
            "status": "COMPLETED",
            "output": {"approval_result": self._state.result},
        }
