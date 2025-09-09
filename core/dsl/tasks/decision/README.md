## 🟢 What is a Decision Task?

Think of a **decision task** as a **switch or a fork in the road** inside your workflow.

* You check a value (like *order type*).
* Based on that value, you decide which path (list of tasks) to follow.
* If the value doesn’t match any path, you fall back to a **default path**.

---

## 🟢 Example in Real Life

Imagine you’re building a workflow to process orders:

* If it’s an **EXPRESS** order → you need to pack fast and ship fast.
* If it’s a **STANDARD** order → you pack normally and ship normally.
* If it’s neither → you just notify the customer.

---

## 🟢 How You Use the Handler

1. **Define the decision task input**
   You give it:

   * a `case_value_param` → the value to check (e.g., `"EXPRESS"`).
   * a `decision_cases` → mapping of possible values to actions.
   * a `default_case` → fallback if nothing matches.

2. **Validate the input**
   The handler checks if the data is valid (are the cases set correctly?).

3. **Execute the decision**
   The handler picks the right case and returns it as the result.

---

## 🟢 In Code (Simplified)

```python
# Step 1: Create the handler
handler = DecisionTaskHandler()

# Step 2: Define the decision task input
input_data = {
    "task_ref_name": "check_order_type",
    "case_value_param": "EXPRESS",
    "decision_cases": {
        "EXPRESS": ["pack_express_order", "ship_express"],
        "STANDARD": ["pack_standard_order", "ship_standard"]
    },
    "default_case": ["notify_customer"]
}

# Step 3: Validate input
validated = handler.validate(input_data)

# Step 4: Run the decision logic
result = await handler.execute(validated)

print(result.output)
# 👉 {"chosen_case": ["pack_express_order", "ship_express"]}
```

---

## 🟢 How to Think About It

* The **decision task** is just like an **“if-else ladder”** inside your workflow.
* Instead of hardcoding it, you **define the rules once** in YAML/JSON.
* The handler just reads the rules and says:
  **“Oh, order is EXPRESS → I’ll choose express tasks.”**

---