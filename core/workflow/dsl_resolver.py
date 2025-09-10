import re
from typing import Any, Dict, Union, List, Optional
from ..dsl.schema import TaskModel

class DSLResolver:
    """Resolves placeholders in task inputs using workflow DSL context."""

    PLACEHOLDER_PATTERN = re.compile(r"\$\{([^\}]+)\}")

    def __init__(self, dsl: Dict[str, Any]):
        self.dsl = dsl
        # Prepare workflow-level inputs
        self.workflow_inputs = self._prepare_workflow_inputs()

    def _prepare_workflow_inputs(self) -> Dict[str, Any]:
        """Prepare workflow input values (defaults as None if not provided)."""
        inputs = {}
        for param in self.dsl.get("inputParameters", []):
            inputs[param] = self.dsl.get("inputValues", {}).get(param)
        return inputs

    def resolve_path(
        self,
        expression: str,
        runtime_task_map: Optional[Dict[str, TaskModel]] = None,
    ) -> Any:
        """
        Resolve expression like:
          - inputParameters.order_id
          - task1.output.created_at
        """
        parts = expression.split(".")
        if not parts:
            return f"<INVALID:{expression}>"

        if parts[0] == "inputParameters":
            return self._traverse_dict(self.workflow_inputs, parts[1:], expression)

        # check runtime task map (preferred)
        if runtime_task_map and parts[0] in runtime_task_map:
            task = runtime_task_map[parts[0]]
            return self._traverse_dict(task.output.model_dump(), parts[1:], expression)

        return f"<UNKNOWN:{expression}>"

    def _traverse_dict(self, data: Any, keys: List[str], expression: str) -> Any:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return f"<MISSING:{expression}>"
        return current

    def substitute(self, value: dict[str, Any], runtime_task_map: Optional[Dict[str, TaskModel]] = None) -> Any:
        """Recursively substitute placeholders inside strings, dicts, and lists."""

        if isinstance(value, str):
            def replacer(match):
                expr = match.group(1)
                return str(self.resolve_path(expr, runtime_task_map))

            return self.PLACEHOLDER_PATTERN.sub(replacer, value)

        elif isinstance(value, dict):
            return {k: self.substitute(v, runtime_task_map) for k, v in value.items()}

        elif isinstance(value, list):
            return [self.substitute(v, runtime_task_map) for v in value]

        return value

    def resolve(
        self,
        task: TaskModel,
        runtime_task_map: Optional[Dict[str, TaskModel]] = None,
    ) -> Any:
        """Public entrypoint for substitution, using the latest task_map."""
        return self.substitute(task.input, runtime_task_map)