from temporalio import activity


def make_activity(task_type: str, handler_cls):
    """Dynamically creates a Temporal activity for a given task type and handler class."""
    @activity.defn(name=f"{task_type.upper()}_TASK")
    async def _activity(payload: dict):
        handler = handler_cls()
        validated = handler.validate(payload)
        result = await handler.execute(validated)
        return result
    return _activity
