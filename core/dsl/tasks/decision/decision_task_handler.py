# Description: Decision task handler with operator support for workflow engine
from ...schema import TaskInput, DSLModel
from pydantic import Field, model_validator
from typing import Dict, List, Optional
import re
import operator
from ..base_task_handler import BaseTaskHandler
from ...schema import TaskResult

class DecisionTaskInput(TaskInput):

    """Strict input model for a decision task with operator support."""

    case_value_param: str = Field(..., description="The key to select the decision case.")
    decision_cases: Dict[str, List[str]] = Field(
        ..., description="Mapping of conditions to their corresponding actions."
    )
    default_case: Optional[List[str]] = Field(
        default_factory=list, description="Actions to take if no case matches."
    )

    _op_pattern = re.compile(r"^(<=|>=|<|>|==|=)?\s*[\w\d\.\-]+$")

    @model_validator(mode="after")
    def validate_cases(self) -> "DecisionTaskInput":
        """Ensure decision_cases keys are valid and default_case is provided if needed."""
        decision_cases = self.decision_cases or {}
        default_case = self.default_case or []

        # Validate keys
        for key in decision_cases.keys():
            if not self._op_pattern.match(str(key)):
                raise ValueError(f"Invalid decision case key: '{key}'")

        if not decision_cases and not default_case:
            raise ValueError(
                "decision_cases cannot be empty unless default_case is provided."
            )

        return self





class DecisionTaskHandler(BaseTaskHandler):
    """Handler for decision tasks in the workflow."""

    OPERATORS = {
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "=": operator.eq,
        "==": operator.eq,
    }

    def validate(self, data: Dict[str, object]) -> DecisionTaskInput:
        return DecisionTaskInput(**data)

    async def execute(self, data: DecisionTaskInput) -> TaskResult:
        """Execute the decision task logic with operator support.

        Args:
            data (DecisionTaskInput): Validated decision task input.
            workflow_input (Dict[str, object]): Workflow-level inputParameters.

        Returns:
            TaskResult: Decision execution result.
        """
        # Read parameter from workflow input
        param_value = data.inputValues.get(data.case_value_param)
        chosen: List[str] = data.default_case

        if param_value is None:
            return TaskResult(
                task_ref_name=data.task_ref_name,
                status="FAILED",
                output={"error": f"Missing inputParameter: {data.case_value_param}"}
            )

        for case_expr, actions in data.decision_cases.items():
            case_expr = case_expr.strip()

            # Check if starts with an operator
            for op_symbol, op_func in self.OPERATORS.items():
                if case_expr.startswith(op_symbol):
                    try:
                        threshold = float(case_expr[len(op_symbol):].strip())
                        if op_func(float(param_value), threshold):
                            chosen = actions
                    except ValueError:
                        continue
                    break
            else:
                # Fallback to direct equality check
                if str(param_value) == case_expr:
                    chosen = actions

            if chosen != data.default_case:
                break

        return TaskResult(
            task_ref_name=data.task_ref_name,
            status="COMPLETED",
            output={"next_task": chosen},
        )
