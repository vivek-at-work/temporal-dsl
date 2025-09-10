from __future__ import annotations

from typing import List, Dict, Optional

from temporalio import workflow

from ..dsl.schema import TaskModel, DSLModel
from .context_updater import ContextUpdater
from .executor_registry import ExecutorRegistry
from .next_task_resolver import NextTaskResolver
from .dsl_resolver import DSLResolver

class WorkflowOrchestrator:
    """Core engine that runs tasks per the DSL, using injected strategies."""
    def __init__(self, registry: ExecutorRegistry) -> None:
        """Initializes with an executor registry."""
        self._registry = registry


    async def run(self, tasks: List[TaskModel], dsl: DSLModel) -> None:
        """Runs the workflow tasks in sequence, applying results and resolving next tasks."""
        if not tasks:
            workflow.logger.info("No tasks in DSL.")
            return

        task_map: Dict[str, TaskModel] = {t.taskReferenceName: t for t in tasks}
        current: Optional[TaskModel] = tasks[0]

        while current:
            resolver = DSLResolver(dsl.model_dump())
            workflow.logger.info("Resolving Task Input task '%s' and task_map '%s'", current.taskReferenceName, task_map)

            current.input = resolver.resolve(current,task_map)
            executor = self._registry.get(current.type)
            if not executor:
                workflow.logger.error("No executor for task type '%s'. Ending.", current.type)
                break
            workflow.logger.info("Executing task '%s' of type '%s'", current.taskReferenceName, current.type)

            result = await executor.execute(current, dsl)
            workflow.logger.info("RESULT: %s", result)

            # Apply result
            ContextUpdater.apply(current, result)

            # Decide next
            next_ref = NextTaskResolver.resolve(current, result)
            if next_ref:
                current = task_map.get(next_ref)
                if not current:
                    workflow.logger.info("Next task '%s' not found. Ending.", next_ref)
                    break
            else:
                idx = tasks.index(current)
                current = tasks[idx + 1] if idx + 1 < len(tasks) else None
