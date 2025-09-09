from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from temporalio.client import Client
import os
app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/",response_class=HTMLResponse)
async def root(request: Request):

    """
    Render HTML form with workflowId and radio buttons for decision.
    """
    return templates.TemplateResponse(
        "decision.html",
        {"request": request}
    )

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")

@app.post("/decision", response_class=HTMLResponse)
async def decision_endpoint(
        workflow_id: str = Form(...), decision: str = Form(...)
):
    """
    Signal a workflow with approval or rejection.

    Args:
        workflowId (str): The workflow ID to signal.
        decision (str): Decision value must be either 'APPROVED' or 'REJECTED'.

    :return: JSON response with status and decision.
    """
    client = await Client.connect(TEMPORAL_HOST)
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal("human_in_loop_signal", decision)

    return f"<h3>✅ Workflow {workflow_id} has been {decision}</h3>"
