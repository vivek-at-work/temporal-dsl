from __future__ import annotations

from typing import Dict, Optional

from .task_executer import TaskExecutor


class ExecutorRegistry:
    """Maps task.type to executor. Defaults to ActivityTaskExecutor."""
    def __init__(self, default_executor: TaskExecutor) -> None:
        self._default = default_executor
        self._by_type: Dict[str, TaskExecutor] = {}

    def register(self, task_type_upper: str, executor: TaskExecutor) -> None:
        """Registers an executor for a specific task type."""
        self._by_type[task_type_upper] = executor

    def get(self, task_type: Optional[str]) -> TaskExecutor:
        """Retrieves the executor for the given task type, or the default."""
        key = (task_type or "").upper()
        return self._by_type.get(key, self._default)
