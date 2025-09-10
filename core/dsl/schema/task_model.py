from typing import Optional, Dict, Any
from pydantic import constr
from pydantic import BaseModel, Field
from .task_result import TaskResult

class TaskModel(BaseModel):
    """Represents a task definition in a Netflix Conductor workflow.

    Attributes:
        taskReferenceName: Unique reference name for the task.
        name: Name of the task.
        type: Type of the task (e.g., SIMPLE, SUB_WORKFLOW).
        input: Input parameters for the task.
        description: Description of the task.
        optional: Whether the task is optional.
        startDelay: Delay before starting the task, in seconds.
    """
    taskReferenceName: str = Field(..., description="Unique reference name for the task.")
    type: str = Field(..., description="Type of the task (e.g., SIMPLE, SUB_WORKFLOW).")
    input: Optional[Dict[str, Any]] = Field(
        None, description="Input parameters for the task."
    )
    description: Optional[str] = Field(
        None, description="Description of the task."
    )
    optional: Optional[bool] = Field(
        None, description="Whether the task is optional."
    )
    output: Optional[TaskResult] = Field(
        None, description="Output of the task.",
    )
    next_task_ref_name: Optional[str] = Field(
        None, description="Next Task to execute."
    )
