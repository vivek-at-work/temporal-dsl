from typing import Any, Dict
from pydantic import Field
from datetime import datetime, timezone

from ...schema import TaskInput, TaskResult, DSLModel
from ..base_task_handler import BaseTaskHandler


class SetVariableTaskInput(TaskInput):
    """Input model for setting workflow variables.

    Attributes:
        task_ref_name (str): Reference name of the task (inherited from TaskInput).
        variables (Dict[str, Any]): Dictionary of variables to set in the workflow context.
    """

    variables: Dict[str, Any] = Field(
        ..., description="Dictionary of workflow variables to set. "
                         "Supports special key values like '$NOW' for current timestamp."
    )


class SetVariableTaskHandler(BaseTaskHandler):
    """Handler for tasks that set workflow variables."""

    def validate(self, data: Dict[str, Any]) -> SetVariableTaskInput:
        """Validate and parse raw input into a SetVariableTaskInput.

        Args:
            data (Dict[str, Any]): Raw input data for the task.

        Returns:
            SetVariableTaskInput: Parsed and validated task input.
        """
        return SetVariableTaskInput(**data)

    async def execute(self, data: SetVariableTaskInput) -> TaskResult:
        """Execute the set variable task logic.

        Args:
            data (SetVariableTaskInput): Validated task input.

        Returns:
            TaskResult: Result of execution, containing the updated variables.
            :param data:
            :param workflow_input:
        """
        resolved_vars: Dict[str, Any] = {}
        print(data)

        for key, value in data.variables.items():
            if isinstance(value, str) and value.upper() == "$NOW":
                resolved_vars[key] = datetime.now(timezone.utc).isoformat()
            else:
                resolved_vars[key] = value

        return TaskResult(
            task_ref_name=data.task_ref_name,
            status="COMPLETED",
            output={**resolved_vars},
        )
