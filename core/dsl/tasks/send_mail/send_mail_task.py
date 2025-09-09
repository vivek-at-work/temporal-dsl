from typing import List, Optional, Union, Protocol, Dict, Any
from pydantic import Field
from ...schema import TaskInput, TaskResult, DSLModel
from ..base_task_handler import BaseTaskHandler

import os
import re
from sendgrid import SendGridAPIClient, Cc, Bcc, To
from sendgrid.helpers.mail import Mail

def render_template(template: str, context: Dict[str, Any]) -> str:
    """Render a template string with ${...} placeholders using dot-paths into context dict.

    Example:
        template = "Order ${inputParameters.order.id} is ${inputParameters.status}"
        context = {"inputParameters": {"order": {"id": 123}, "status": "shipped"}}
        -> "Order 123 is shipped"
    """

    def get_value(path: str, data: Dict[str, Any]) -> Any:
        """

        :param path:
        :param data:
        :return:
        """
        parts = path.split(".")
        value = data
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return f"<missing:{path}>"
        return value

    pattern = re.compile(r"\$\{([^}]+)\}")

    def replacer(match):
        """

        :param match:
        :return:
        """
        path = match.group(1).strip()
        return str(get_value(path, context))

    return pattern.sub(replacer, template)
# =====================
# Input Schema
# =====================
class SendEmailTaskInput(TaskInput):
    """Strict input model for a send email task."""

    to: Union[str, List[str]] = Field(..., description="Recipient(s) of the email.")
    subject: str = Field(..., description="Subject line of the email.")
    body: str = Field(..., description="Email body (plain text or HTML).")
    cc: Optional[Union[str, List[str]]] = Field(default_factory=list, description="CC recipients.")
    bcc: Optional[Union[str, List[str]]] = Field(default_factory=list, description="BCC recipients.")


# =====================
# Provider Interface
# =====================
class EmailProvider(Protocol):
    """Protocol for pluggable email providers."""

    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> dict:
        ...


# =====================
# SendGrid Provider
# =====================
class SendGridProvider:
    """SendGrid email provider implementation."""

    def __init__(self, api_key: str, from_email: str):
        self.client = SendGridAPIClient(api_key)
        self.from_email = from_email

    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> dict:
        """

        :param to:
        :param subject:
        :param body:
        :param cc:
        :param bcc:
        :return:
        """
        message = Mail(
            from_email=self.from_email,
            to_emails=[To(email) for email in to],
            subject=subject,
            html_content=body,
        )

        if cc:
            message.cc = [Cc(email) for email in cc]
        if bcc:
            message.bcc = [Bcc(email) for email in bcc]

        response = self.client.send(message)
        return {"status_code": response.status_code, "body": response.body}

# =====================
# Console Provider (Fallback)
# =====================
class ConsoleEmailProvider:
    """Fallback email provider that prints email details to the console."""

    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> dict:
        print("\n[EmailProvider] Console Fallback")
        print("===================================")
        print(f"To: {', '.join(to)}")
        if cc:
            print(f"CC: {', '.join(cc)}")
        if bcc:
            print(f"BCC: {', '.join(bcc)}")
        print(f"Subject: {subject}")
        print("------------ Body ---------------")
        print(body)
        print("===================================\n")

        return {"status_code": 200, "body": "Rendered to console"}



# =====================
# Provider Factory
# =====================
def get_email_provider() -> EmailProvider:
    """Factory to select the email provider via env/config."""
    provider = os.getenv("EMAIL_PROVIDER", "sendgrid").lower()

    if provider == "sendgrid":
        return SendGridProvider(
            api_key=os.getenv("SENDGRID_API_KEY"),
            from_email=os.getenv("SENDGRID_FROM_EMAIL", "no-reply@example.com"),
        )
    # elif provider == "ses":
    #     return SESProvider(...)
    # elif provider == "smtp":
    #     return SMTPProvider(...)
    else:
        return ConsoleEmailProvider()


# =====================
# Task Handler
# =====================
class SendEmailTaskHandler(BaseTaskHandler):
    """Handler for sending emails in the workflow with pluggable providers."""

    def validate(self, data: dict) -> SendEmailTaskInput:
        return SendEmailTaskInput(**data)

    async def execute(self, data: SendEmailTaskInput) -> TaskResult:
        """Execute the send email task with the configured provider."""
        to = data.to if isinstance(data.to, list) else [data.to]
        cc = data.cc if isinstance(data.cc, list) else ([data.cc] if data.cc else [])
        bcc = data.bcc if isinstance(data.bcc, list) else ([data.bcc] if data.bcc else [])
        provider = get_email_provider()

        try:
            result = await provider.send_email(to,data.subject,data.body, cc, bcc)
            status = "COMPLETED" if 200 <= result.get("status_code", 500) < 300 else "FAILED"

            return TaskResult(
                task_ref_name=data.task_ref_name,
                status=status,
                output={
                    "to": to,
                    "subject": data.subject,
                    "provider": provider.__class__.__name__,
                    "status_code": result.get("status_code"),
                },
            )
        except Exception as e:
            return TaskResult(
                task_ref_name=data.task_ref_name,
                status="FAILED",
                output={"error": str(e)},
            )
