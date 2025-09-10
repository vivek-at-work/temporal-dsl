from typing import Dict, Any, Optional

from pydantic import BaseModel


class TaskInput(BaseModel):
    """
    Represents the input required for a task, including its reference name.

    Attributes:
        task_ref_name (str): The reference name of the task.
    """
    task_ref_name: str



