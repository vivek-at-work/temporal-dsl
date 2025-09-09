from .tasks import (HttpTaskHandler, SetVariableTaskHandler, DecisionTaskHandler,
                        SendEmailTaskHandler,ApprovalTaskHandler)
task_registry = {
    "http": HttpTaskHandler,
    "set_variable": SetVariableTaskHandler,
    "decision": DecisionTaskHandler,
    "send_mail": SendEmailTaskHandler,
    "approval": ApprovalTaskHandler,
}