from typing import Optional, Dict, Any, Literal
from ..base_task_handler import BaseTaskHandler
from ...schema import TaskInput, TaskResult,DSLModel
from pydantic import HttpUrl, Field
import requests


class HttpTaskInput(TaskInput):
    """Input model for HTTP tasks.

    Attributes:
        task_ref_name (str): Reference name of the task (inherited from TaskInput).
        url (HttpUrl): The URL to send the HTTP request to.
        method (Literal["GET", "POST", "PUT", "DELETE"]): The HTTP method.
        headers (Optional[Dict[str, str]]): Optional HTTP headers.
        body (Optional[Dict[str, Any]]): Optional JSON request body.
    """

    url: HttpUrl
    method: Literal["GET", "POST", "PUT", "DELETE"]
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Optional HTTP headers."
    )
    body: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional JSON request body."
    )


class HttpTaskHandler(BaseTaskHandler):
    """Handler for executing HTTP tasks."""

    def validate(self, data: Dict[str, Any]) -> HttpTaskInput:
        """Validate and parse raw input into a HttpTaskInput.

        Args:
            data (Dict[str, Any]): Raw input data for the HTTP task.

        Returns:
            HttpTaskInput: Parsed and validated input model.
        """
        return HttpTaskInput(**data)

    async def execute(self, data: HttpTaskInput) -> TaskResult:
        """Execute the HTTP task using the requests library.

        Args:
            data (HttpTaskInput): The validated HTTP task input.

        Returns:
            TaskResult: The result of the HTTP request execution.
        """
        response = requests.request(
            method=data.method,
            url=str(data.url),
            headers=data.headers or {},
            json=data.body,
        )

        result_data = {
            "status": response.status_code,
            "url": str(data.url),
            "method": data.method,
            "body": data.body,
            "response": response.text,
        }

        return TaskResult(
            task_ref_name=data.task_ref_name,
            status="COMPLETED",
            output=result_data,
        )
