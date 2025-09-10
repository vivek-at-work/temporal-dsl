# Description: Decision task handler with operator support for workflow engine
from ...schema import TaskInput
from pydantic import Field, model_validator
from typing import Dict, List, Optional, Any
import re
import operator
from ..base_task_handler import BaseTaskHandler
from ...schema import TaskResult
class DecisionTaskInput(TaskInput):
    """Strict input model for a decision task with operator + logical support."""

    param_value: Any = Field(..., description="The key to select the decision case.")
    decision_cases: Dict[str, List[str]] = Field(
        ..., description="Mapping of conditions to their corresponding actions."
    )
    default_case: Optional[List[str]] = Field(
        default_factory=list, description="Actions to take if no case matches."
    )

    # Updated regex: allow operators, words, numbers, dots, dashes, and logical keywords
    _op_pattern = re.compile(
        r"^([<>=!]=?|==)?\s*[\w\d\.\-]+(\s+(AND|OR|NOT)\s+([<>=!]=?|==)?\s*[\w\d\.\-]+)*$",
        re.IGNORECASE,
    )

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
    """Handler for decision tasks in the workflow with extended logical operator support."""

    OPERATORS = {
        "<=": operator.le,
        ">=": operator.ge,
        "==": operator.eq,
        "=": operator.eq,
        "<": operator.lt,
        ">": operator.gt,
    }

    LOGICAL_KEYWORDS = {"AND", "OR", "NOT"}

    def validate(self, data: Dict[str, object]) -> DecisionTaskInput:
        return DecisionTaskInput(**data)

    def _try_number(self, value: Any) -> Any:
        """Try to convert a value to int/float, else return original string."""
        try:
            if "." in str(value):
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return str(value)

    def _evaluate_expression(self, param_value: Any, expr: str) -> bool:
        """
        Evaluate a single logical/relational expression.
        Supports AND, OR, NOT combined with numeric or string comparisons.
        """
        print(f"[DEBUG] Evaluating expr={expr!r} against param_value={param_value!r}")

        def _try_number(value: Any) -> Any:
            """Convert to int/float if possible, else return original string."""
            if value is None:
                return None
            try:
                if isinstance(value, str) and "." in value:
                    return float(value)
                return int(value)
            except (ValueError, TypeError):
                return str(value).strip()

        param_value = _try_number(param_value)

        # Tokenize by logical operators
        tokens = re.split(r"\s+(AND|OR|NOT)\s+", expr.strip(), flags=re.IGNORECASE)

        def eval_token(token: str) -> bool:
            token = token.strip()
            if not token:
                return False

            # Handle NOT explicitly
            if token.upper().startswith("NOT "):
                return not eval_token(token[4:].strip())

            # Operator-based check
            for op_symbol, op_func in sorted(self.OPERATORS.items(), key=lambda x: -len(x[0])):
                if token.startswith(op_symbol):
                    threshold_str = token[len(op_symbol):].strip()
                    threshold = _try_number(threshold_str)
                    print(f"[DEBUG] Comparing {param_value} {op_symbol} {threshold}")
                    try:
                        return op_func(param_value, threshold)
                    except Exception:
                        return False

            # Equality fallback
            return str(param_value) == token or param_value == _try_number(token)

        # Sequential evaluation with short-circuiting
        result = eval_token(tokens[0])
        i = 1
        while i < len(tokens):
            logical = tokens[i].upper()
            next_val = eval_token(tokens[i + 1])

            if logical == "AND":
                result = result and next_val
            elif logical == "OR":
                # short-circuit: if already True, stay True
                result = result or next_val

            i += 2

        return result

    async def execute(self, data: DecisionTaskInput) -> TaskResult:
        """Execute the decision task logic with operator + logical support."""
        param_value = self._try_number(data.param_value)
        chosen: List[str] = data.default_case
        print(f"[DEBUG] Raw param_value={param_value!r}, type={type(param_value)}")
        if param_value is None:
            return TaskResult(
                task_ref_name=data.task_ref_name,
                status="FAILED",
                output={"error": "Missing inputParameter"}
            )

        for case_expr, actions in data.decision_cases.items():
            if self._evaluate_expression(param_value, case_expr):
                chosen = actions
                break

        return TaskResult(
            task_ref_name=data.task_ref_name,
            status="COMPLETED",
            output={"next_task": chosen},
        )

