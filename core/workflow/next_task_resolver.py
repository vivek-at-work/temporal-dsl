from __future__ import annotations

from typing import Dict, Any, Optional, Union, Iterable

from ..dsl.schema import TaskModel


class NextTaskResolver:
    """Resolves next task ref name from result or task."""
    @staticmethod
    def resolve(task: TaskModel, result: Dict[str, Any]) -> Optional[str]:
        """ Determines the next task reference name."""
        output = result.get("output") or {}
        next_from_output: Optional[Union[str, Iterable[str]]] = output.get("next_task")
        next_from_task: Optional[Union[str, Iterable[str]]] = getattr(task, "next_task_ref_name", None)
        candidate = next_from_output if next_from_output else next_from_task
        if not candidate:
            return None
        if isinstance(candidate, (list, tuple)):
            return candidate[0] if candidate else None
        return str(candidate)
