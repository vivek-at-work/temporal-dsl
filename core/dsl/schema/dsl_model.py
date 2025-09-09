from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

from .task_model import TaskModel


class DSLModel(BaseModel):
    """Represents a Netflix Conductor workflow definition.

    Attributes:
        name: Name of the workflow.
        description: Description of the workflow.
        version: Version of the workflow.
        tasks: List of tasks in the workflow.
        inputParameters: List of input parameter names.
        outputParameters: Output parameters mapping.
    """
    name: str = Field(..., description="Name of the workflow.")
    description: Optional[str] = Field(
        None, description="Description of the workflow."
    )
    version: Optional[str] = Field(
        None, description="Version of the workflow."
    )
    tasks: List[TaskModel] = Field(
        ..., description="List of tasks in the workflow."
    )
    inputParameters: Optional[List[str]] = Field(
        None, description="List of input (Workflow-level inputs)."
    )
    outputParameters: Optional[Dict[str, Any]] = Field(
        None, description="Workflow-level outputs, often mapped from task outputs.."
    )
    inputValues: Optional[Dict[str, Any]] = Field(
        None, description="Input values for the workflow execution."
    )


