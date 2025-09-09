

## 📌 Sample Node Definition (YAML/DSL)

Now workflow authors can write:

```yaml
name: "user_registration_workflow"
tasks:
  - taskReferenceName: "init_user_state"
    name: "set_variables"
    type: "SET_VARIABLE"
    inputParameters:
      task_ref_name: "init_user_state"
      variables:
        is_verified: false
        role: "customer"
        created_at: "$NOW"
```

---

## 📊 Example Usage in Python

```python
handler = SetVariableTaskHandler()

input_data = {
    "task_ref_name": "init_user_state",
    "variables": {
        "is_verified": False,
        "role": "customer",
        "created_at": "$NOW"
    },
}

validated = handler.validate(input_data)
result = await handler.execute(validated)

print(result.output)
# 👉 {
#   "set_variables": {
#     "is_verified": False,
#     "role": "customer",
#     "created_at": "2025-08-31T07:45:10.123456+00:00"
#   }
# }
```

---

## 🟢 Simple Explanation

* Workflow defines `created_at: "$NOW"`.
* When executed, the handler **detects `$NOW` and replaces it with the current UTC timestamp**.
* No need to hardcode timestamps — always fresh at runtime.

---
