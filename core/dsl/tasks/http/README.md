


## 📌 Sample Node Definition (YAML/DSL)

Here’s how you would define an **HTTP task** node in a workflow:

```yaml
name: "notify_customer_workflow"
description: "Workflow to notify customer via HTTP API"
version: 1
tasks:
  - taskReferenceName: "send_notification"
    name: "http_notify"
    type: "HTTP"
    inputParameters:
      task_ref_name: "send_notification"
      url: "https://api.example.com/notify"
      method: "POST"
      headers:
        Content-Type: "application/json"
        Authorization: "Bearer xyz"
      body:
        message: "Your order has been shipped"
```

---

## 📊 Example Usage in Python

```python
handler = HttpTaskHandler()

input_data = {
    "task_ref_name": "send_notification",
    "url": "https://api.example.com/notify",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": {"message": "Your order has been shipped"}
}

# Step 1: Validate
validated = handler.validate(input_data)

# Step 2: Execute (makes real HTTP call)
result = await handler.execute(validated)

print(result.output)
# {
#   "status": 200,
#   "url": "https://api.example.com/notify",
#   "method": "POST",
#   "body": {"message": "Your order has been shipped"},
#   "response": "{...response from server...}"
# }
```

---

## 🟢 Simple Explanation

* **This handler is like a mini HTTP client in your workflow.**
* You tell it: *“make a POST to this URL with these headers and body”*.
* It makes the request, then returns the result (status, response body, etc.) back to the workflow.

---

👉 Do you want me to also extend this to **support retries & timeouts** (e.g., configurable max retries, exponential backoff), since HTTP tasks often need resilience?
