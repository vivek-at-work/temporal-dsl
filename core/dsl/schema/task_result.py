from typing import Optional, Dict, Any
from pydantic import constr, BaseModel


class TaskResult(BaseModel):
    """
    Represents the result of a task execution.

    Attributes:
        task_ref_name (str): Reference name of the task.
        status (str): Status of the task. One of 'COMPLETED', 'FAILED', 'IN_PROGRESS', or 'TERMINATED'.
        output (Dict[str, Any]): Output data produced by the task.
        reason (Optional[str]): Optional reason for the task status, typically used for failures.
    """
    task_ref_name: str
    status: constr(pattern="^(COMPLETED|FAILED|IN_PROGRESS|TERMINATED)$")
    output: Dict[str, Any]
    reason: Optional[str] = None
