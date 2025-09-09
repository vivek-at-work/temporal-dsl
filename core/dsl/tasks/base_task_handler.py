from abc import ABC, abstractmethod
from typing import Dict, Any
from ..schema import TaskInput, TaskResult, DSLModel


class BaseTaskHandler(ABC):
    """
    Abstract base class for task handlers.

    Defines the interface for validating input data and executing tasks.
    """

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> TaskInput:
        """
        Validate the input data and return a TaskInput instance.

        Args:
            data (Dict[str, Any]): The input data to validate.

        Returns:
            TaskInput: The validated task input.

        Raises:
            ValueError: If the input data is invalid.
        """
        ...

    @abstractmethod
    async def execute(self, data: TaskInput) -> TaskResult:
        """
        Execute the task using the provided TaskInput.

        Args:
            data (TaskInput): The validated task input.

        Returns:
            Dict[str, Any]: The result of the task execution.
            :param dsl:
            :param data:
        """
        ...
