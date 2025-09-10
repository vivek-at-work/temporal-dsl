from ..base_task_handler import BaseTaskHandler
from ...schema import TaskResult

from typing import Optional
from pydantic import Field
from ...schema import TaskInput,DSLModel

class ApprovalTaskInput(TaskInput):
    """Input model for a simple approval task."""

    message: str = Field(..., description="Approval message shown to the approver.")
    timeout: Optional[int] = Field(
        default=3600, description="How long to wait (in seconds) before timing out."
    )


class ApprovalTaskHandler(BaseTaskHandler):
    """Handler for a simple human approval task."""

    def validate(self, data: dict) -> ApprovalTaskInput:
        return ApprovalTaskInput(**data)

    async def execute(self, data: ApprovalTaskInput) -> TaskResult:
        # In real flow: you'd pause the workflow and wait for a signal
        return TaskResult(
            task_ref_name=data.task_ref_name,
            status="COMPLETED",
            output={
                "message": data.message,
                "timeout": data.timeout,
            },
        )
