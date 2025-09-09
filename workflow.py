"""
DSL-driven Temporal Workflow, decomposed into small SOLID classes.

- WorkflowOrchestrator: controls the run loop
- TaskExecutor Protocol + ExecutorRegistry: open/closed for task types
- ActivityTaskExecutor: default activity-backed executor
- ApprovalTaskExecutor: signal-based executor (APPROVAL)
- NextTaskResolver: isolates next-task selection
- PayloadBuilder: isolates payload normalization
- ContextUpdater: isolates context/status/output updates
- ApprovalSignalState: DI carrier for approval results & wait
"""

from __future__ import annotations

from typing import Any, Dict, List

from temporalio import workflow
from core.dsl.dsl_parser import DSLParser
from core.dsl.schema import TaskModel
from core.workflow.activity_task_executer import ActivityTaskExecutor
from core.workflow.human_in_loop_signal_state import HumanInLoopSignalState
from core.workflow.human_in_loop_task_executor import HumanInLoopTaskExecutor
from core.workflow.executor_registry import ExecutorRegistry
from core.workflow.workflow_orchestrator import WorkflowOrchestrator

@workflow.defn
class DSLWorkflow:
    """Temporal Workflow entry point; delegates to orchestrator."""

    def __init__(self) -> None:
        self._human_in_loop_signal = HumanInLoopSignalState()
        default_exec = ActivityTaskExecutor()
        self._registry = ExecutorRegistry(default_executor=default_exec)
        self._registry.register("APPROVAL", HumanInLoopTaskExecutor(self._human_in_loop_signal))
        self._orchestrator = WorkflowOrchestrator(registry=self._registry)

    @workflow.signal
    async def human_in_loop_signal(self, result: str) -> None:
        """Signal: set an approval decision for a pending APPROVAL task."""
        self._human_in_loop_signal.result = result

    @workflow.run
    async def run(self, data: Dict[str, Any]) -> str:
        """Run the DSL workflow."""
        parser = DSLParser(data)
        tasks: List[TaskModel] = parser.get_tasks()
        await self._orchestrator.run(tasks=tasks, dsl=parser.dsl)
        return "workflow_completed"
