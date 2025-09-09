from typing import List, Dict, Any, Optional
from .schema import DSLModel, TaskModel


class DSLParser:
    """Parses and validates a Netflix Conductor DSL using Pydantic models.

    Args:
        data: Dictionary representing the workflow DSL.
    """

    def __init__(self, data: Dict[str, Any]):
        """Initializes the parser and validates the DSL."""
        self.dsl = DSLModel.model_validate(data)

    def get_tasks(self) -> List[TaskModel]:
        """Returns the list of tasks in the workflow.

        Returns:
            List of TaskModel objects.
        """
        return self.dsl.tasks

    def find_task_by_ref(self, ref: str) -> Optional[TaskModel]:
        """Finds a task by its reference name.

        Args:
            ref: The task reference name.

        Returns:
            The TaskModel if found, else None.
        """
        return next((t for t in self.dsl.tasks if t.taskReferenceName == ref), None)
