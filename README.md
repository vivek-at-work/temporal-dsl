## 🧭 Architecture Summary 

This system implements a **DSL-driven workflow orchestration platform** using **Temporal** with explicit support for **human-in-the-loop approvals**.

### One-Line Mental Model
```code
DSL defines intent → Workflow orchestrates → Worker executes → API signals decisions
```

### Key Concepts

* **DSL as Intent**

  * Workflows are defined declaratively (JSON/YAML).
  * The DSL expresses *what* should happen, not *how* it is executed.

* **Workflow as Orchestrator**

  * `DSLWorkflow` interprets the DSL and controls execution order.
  * All control flow is deterministic and replay-safe.

* **Activities as Side Effects**

  * External actions (HTTP, email, variable mutation) are isolated in activities.
  * Activities provide retries, timeouts, and fault isolation.

* **Signals for Human Interaction**

  * Approvals and rejections enter the system via Temporal signals.
  * No polling, no external state checks, no blocking threads.

* **FastAPI as Control Plane**

  * The API layer exposes simple endpoints for humans or systems.
  * It never executes business logic—only signals workflows.

### Why This Architecture Works

* Scales to long-running workflows (minutes → months)
* Fully auditable execution history
* Clean separation of concerns
* Easy to extend with new DSL task types
* Aligns with Temporal best practices for determinism and reliability

In short: **DSL defines intent, Temporal guarantees execution, FastAPI enables control.**
```code
+-----------------------------------------------------------+
|                       External Actors                     |
|                                                           |
|   +-------------------+        +----------------------+   |
|   | Human / System    |        | curl / REST Client   |   |
|   +---------+---------+        +----------+-----------+   |
|             |                               |               |
+-------------|-------------------------------|---------------+
              v                               v
+-----------------------------------------------------------+
|                       API Layer                           |
|                                                           |
|   +---------------------------------------------------+   |
|   |           FastAPI App (app.py)                    |   |
|   |                                                   |   |
|   |   /approval   /rejection   (Temporal Signals)     |   |
|   +------------------------+--------------------------+   |
|                            |                              |
+----------------------------|------------------------------+
                             v
+-----------------------------------------------------------+
|                    Temporal Platform                      |
|                                                           |
|   +--------------------+       +----------------------+   |
|   | Temporal Server    |<----->| Temporal Web UI      |   |
|   |  localhost:7233   |       |  localhost:8080      |   |
|   +---------+----------+       +----------------------+   |
|             |                                              |
+-------------|----------------------------------------------+
              |
              v
+-----------------------------------------------------------+
|                   Execution Layer                         |
|                                                           |
|   +--------------------+                                  |
|   | DSLWorkflow        |  (workflow.py)                   |
|   |  - Orchestration   |                                  |
|   |  - Signal Handling |                                  |
|   +---------+----------+                                  |
|             |                                             |
|             | schedules                                  |
|             v                                             |
|   +--------------------+       +----------------------+   |
|   | Temporal Worker    |-----> | Activities           |   |
|   | (worker.py)        |       | (core/activities)    |   |
|   +--------------------+       +----------------------+   |
|                                                           |
+-----------------------------------------------------------+

+-----------------------------------------------------------+
|                     Domain Layer                          |
|                                                           |
|   +--------------------+                                  |
|   | DSL Definition     |  (JSON / YAML)                   |
|   +---------+----------+                                  |
|             |                                             |
|             v                                             |
|   +--------------------+                                  |
|   | DSL Parser         |  (core/dsl)                      |
|   +---------+----------+                                  |
|             |                                             |
|             v                                             |
|   +--------------------+                                  |
|   | Workflow Context   |  (state & variables)             |
|   +--------------------+                                  |
|                                                           |
+-----------------------------------------------------------+

```

# 🧪 How to Run & Test the DSL + Temporal App

## 1) Prerequisites

* **Option A (local install):**

  * Python 3.10+ (3.11 fine)
  * `pip` / `venv`
* **Option B (containerized):**

  * Docker & Docker Compose

---

## 2) Start Temporal via Docker Compose

Your `docker-compose.yml` already defines the Temporal server. Just run:

```bash
docker-compose up -d
```

This will start Temporal and its dependencies.
Check with:

```bash
docker ps | grep temporal
```

By default Temporal frontend will be on `localhost:7233`.

---

## 3) Local Dev Setup (Python)

If you prefer running locally:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Your `requirements.txt` includes `temporalio==1.13.0`, `fastapi`, `uvicorn`, `pydantic 2.x`, etc.

---

## 4) Run the Worker

The worker listens on `dsl-task-queue` and executes DSL tasks.

```bash
python worker.py
```

---

## 5) Run the FastAPI App (signals)

This exposes `/approval` and `/rejection` endpoints to signal workflows.

```bash
uvicorn app:app --reload --port 8000
```

Check:

* [http://127.0.0.1:8000](http://127.0.0.1:8000) → should return `{"message": "Hello FastAPI"}`.

---

## 6) Start a Workflow (Client)

Use the client script to kick off a workflow with your DSL definition:

```bash
python client.py
```

This connects to Temporal, starts `DSLWorkflow`, and returns a workflow ID.

---

## 7) Send Approval / Rejection

With the workflow running, call:

```bash
curl "http://127.0.0.1:8000/approval?workflowId=<YOUR_WORKFLOW_ID>"
```

or

```bash
curl "http://127.0.0.1:8000/rejection?workflowId=<YOUR_WORKFLOW_ID>"
```

These hit FastAPI → Temporal client → signal `DSLWorkflow` with APPROVED/REJECTED.

---

## 8) Observe Execution

* Logs in `worker.py` terminal will show DSL task execution.
* Temporal Web UI (if enabled in `docker-compose.yml`) is usually on `http://localhost:8080` — you can inspect workflow history there.

---

✅ **That’s it:**

* `docker-compose up` → bring up Temporal
* `python worker.py` → start worker
* `uvicorn app:app` → API for signals
* `python client.py` → start workflow
* `curl …/approval` → send decisions

---


---

# 📂 Project File Overview

## 1. **`worker.py`**

* **Purpose:** Runs a Temporal worker process.
* **What it does:**

  * Connects to Temporal server at `localhost:7233`.
  * Registers:

    * The `DSLWorkflow` workflow class.
    * All activities found in your `core.activities.registry`.
  * Starts listening on the task queue **`dsl-task-queue`**.
* **Why it matters:**
  Without the worker, Temporal has no executor for your workflow logic or tasks.

---

## 2. **`workflow.py`**

* **Purpose:** Defines the DSL-driven workflow.
* **What it does:**

  * Implements the `DSLWorkflow` class decorated with `@workflow.defn`.
  * Has:

    * `@workflow.run` → main workflow logic that executes tasks from the DSL sequentially.
    * `@workflow.signal approval_signal` → allows external systems (like FastAPI endpoints) to send **APPROVED / REJECTED** signals into the workflow.
  * Uses `DSLParser` to interpret your DSL JSON/YAML and `WorkflowContext` to store state.
* **Why it matters:**
  This is your core orchestration logic, mapping DSL → Temporal execution.

---

## 3. **`app.py`**

* **Purpose:** Exposes HTTP endpoints for external control (via FastAPI).
* **What it does:**

  * Defines FastAPI app with routes:

    * `/approval?workflowId=<id>` → sends `approval_signal` with `"APPROVED"`.
    * `/rejection?workflowId=<id>` → sends `approval_signal` with `"REJECTED"`.
    * Root `/` → returns a hello message (health check).
  * Connects to Temporal to get a workflow handle and send the signal.
* **Why it matters:**
  Provides a **simple API interface** so humans or other services can approve/reject workflows.

---

## 4. **`client.py`**

* **Purpose:** Starts a new workflow execution.
* **What it does:**

  * Connects to Temporal.
  * Loads a DSL workflow definition (JSON/dict).
  * Starts the `DSLWorkflow` with:

    * Workflow ID: `workflow-<uuid>`
    * Task queue: `dsl-task-queue`
  * Prints the started workflow ID.
* **Why it matters:**
  This is the **entrypoint** to trigger workflows.

---

## 5. **`requirements.txt`**

* **Purpose:** Lists Python dependencies.
* **Highlights:**

  * `temporalio==1.13.0` → Temporal Python SDK.
  * `fastapi`, `uvicorn`, `starlette` → API layer.
  * `pydantic==2.11.7` → data validation for DSL schemas.
  * `requests`, `xmltodict`, `protobuf`, etc. → activity helpers.
* **Why it matters:**
  Ensures your environment has all matching versions.

---

## 6. **`docker-compose.yml`**

* **Purpose:** Spins up the Temporal service cluster with Docker.
* **What it does (usually):**

  * Starts **Temporal server** (frontend, history, matching, worker).
  * Starts **dependencies** (like Cassandra/MySQL/Postgres & ElasticSearch).
  * Optionally starts **Temporal Web UI** (for inspecting workflows).
* **Why it matters:**
  Gives you a ready-to-use Temporal backend for local dev/test.

---

Here’s a **README-style explanation** that includes the logic from your uploaded code (`worker.py`, `workflow.py`, `app.py`, `client.py`) and the unpacked `core/` module you zipped. I’ll describe the moving parts so anyone can understand how this app works end-to-end.

---

# 📝 DSL + Temporal Workflow Orchestration

This project demonstrates how to run **DSL-driven workflows** on [Temporal](https://temporal.io) using the Python SDK, with external human approvals via FastAPI.

---

## 📂 Code Structure

### 1. **`core/` (domain logic)**

* **`core/dsl/`** → contains the DSL parser (`dsl_parser.py`) and schema (`schema.py`) that translate JSON DSL definitions into strongly typed models (`DSLModel`, `TaskModel`, etc.).
* **`core/activities/`** → actual task implementations. Examples:

  * **SET\_VARIABLE\_TASK**: updates workflow variables.
  * **HTTP\_TASK**: makes HTTP calls.
  * **DECISION\_TASK**: branches workflow execution based on input values.
  * **APPROVAL\_TASK**: pauses execution until a signal arrives.
  * **send\_mail\_TASK**: simulates sending an email.
* **`core/task_registry.py`** → maps task types (e.g., `SET_VARIABLE`, `HTTP`, `DECISION`) to their handler classes.
* **`core/activities/make_activity`** → utility to wrap handler classes into Temporal activities.

👉 This is the **business logic layer**. You can add new DSL task types here and they automatically become usable.

---

### 2. **`workflow.py`**

* Defines the `DSLWorkflow` class (`@workflow.defn`).
* Runs tasks parsed from DSL sequentially.
* Handles approvals:

  * When it encounters an **APPROVAL** task, it pauses and waits for a signal.
  * Signals (`approval_signal`) are sent externally via API.
* Uses `WorkflowContext` to track variables and state.

👉 This is the **orchestration layer**.

---

### 3. **`worker.py`**

* Connects to Temporal at `localhost:7233`.
* Registers:

  * The `DSLWorkflow` workflow.
  * All activities defined in `core.task_registry`.
* Listens on task queue: **`dsl-task-queue`**.

👉 This is the **execution engine** — runs workflows and executes activities.

---

### 4. **`client.py`**

* Defines a sample **DSL JSON** for an order processing workflow:

  * Sets variables.
  * Makes branching decisions (`DECISION`).
  * Sends HTTP requests.
  * Sends emails.
  * Requests approval before finalizing.
* Connects to Temporal and starts a workflow execution with this DSL.

👉 This is the **workflow starter**.

---

### 5. **`app.py`**

* Exposes REST API endpoints with **FastAPI**:

  * `/approval?workflowId=...` → signals `"APPROVED"`.
  * `/rejection?workflowId=...` → signals `"REJECTED"`.
* Connects to Temporal and signals the running workflow.

👉 This is the **human-in-the-loop interface**.

---

### 6. **`requirements.txt`**

* Lists pinned dependencies:

  * `temporalio==1.13.0` → Temporal Python SDK
  * `fastapi`, `uvicorn` → API server
  * `pydantic 2.x` → DSL schema validation
  * `requests`, `xmltodict` → helper libs for activities

---

### 7. **`docker-compose.yml`**

* Spins up a local Temporal cluster with dependencies.
* Lets you run everything without installing Temporal separately.



---

## 🔄 How Everything Connects



---

## 🚀 Running the System

1. **Start Temporal**

   ```bash
   docker-compose up -d
   ```

2. **Install deps**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run worker**

   ```bash
   python worker.py
   ```

4. **Start API server**

   ```bash
   uvicorn app:app --reload --port 8000
   ```

5. **Kick off a workflow**

   ```bash
   python client.py
   ```

6. **Send approval / rejection**

   ```bash
   curl "http://127.0.0.1:8000/approval?workflowId=<WORKFLOW_ID>"
   curl "http://127.0.0.1:8000/rejection?workflowId=<WORKFLOW_ID>"
   ```

---


# 🧩 How They Work Together

1. `docker-compose.yml` → boots the Temporal cluster.
2. `worker.py` → registers workflows + activities and waits for jobs.
3. `client.py` → starts a workflow run using your DSL.
4. `workflow.py` → defines how the workflow actually executes tasks and handles signals.
5. `app.py` → exposes REST endpoints to control workflow execution mid-flight.
6. `requirements.txt` → ensures consistent environment setup.

---

