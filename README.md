# Learning Temporal — OCR Workflow Series

A hands-on series of exercises for learning [Temporal](https://temporal.io/) using an OCR (Optical Character Recognition) pipeline as the running example. Each exercise builds on the previous one, introducing a new Temporal concept.

---

## What is Temporal?

Temporal is a **durable workflow engine**. It lets you write long-running, fault-tolerant business logic in plain code. If a worker crashes mid-execution, Temporal replays the workflow from where it left off — no data is lost.

### Core Concepts

| Concept | Description |
|---|---|
| **Workflow** | The orchestrator. Defines the sequence of steps. Must be deterministic — no direct I/O, no `random`, no `datetime.now()`. |
| **Activity** | A single unit of work (the real work: file I/O, HTTP calls, ML inference). Can fail and be retried independently. |
| **Worker** | A process that polls Temporal for tasks and executes workflows and activities. |
| **Task Queue** | A named queue that connects clients → workers. Workers register on a queue; clients submit jobs to a queue. |
| **Client** | Used to submit/start workflows from outside (your `submit_job.py`). |
| **Signal** | A message sent into a running workflow to change its state (e.g. cancel a job). |
| **Query** | A read-only call into a running workflow to inspect its current state (e.g. get progress). |

### The Golden Rule

> Workflows are **orchestrators** — they only call activities.  
> Activities are **executors** — they do the actual work.

---

## Project Structure

```
Temporal_OCR/
├── HelloWorld_Ex_1/          # Exercise 1 — Basic workflow + activity
├── Structured_Data_Ex_2/     # Exercise 2 — Dataclasses as inputs/outputs
├── Retry_Timeout_Ex_3/       # Exercise 3 — Retry policies and timeouts
├── MultiPage_OCR_Ex_4/       # Exercise 4 — Parallel activities with asyncio.gather
├── Child_Workflows_Ex_5/     # Exercise 5 — Parent/child workflows
├── Workflow_Signals_Ex_6/    # Exercise 6 — Signals and queries
├── External_Service_Ex_7/    # Exercise 7 — Calling an external HTTP service (Triton)
├── ocr_env/                  # Python virtual environment
└── requirements.txt
```

Each exercise folder contains:
- `workflow.py` — workflow definition
- `activity.py` — activity implementation
- `worker.py` — starts the worker process
- `submit_job.py` — client that triggers the workflow
- `data_model.py` — dataclass/pydantic models (from Ex 2 onward)

---

## Setup

### Prerequisites

- Python 3.9+
- [Temporal CLI](https://docs.temporal.io/cli) — install via Homebrew:

```bash
brew install temporal
```

### Install Python Dependencies

```bash
cd Temporal_OCR
python -m venv ocr_env
source ocr_env/bin/activate
pip install -r requirements.txt
```

---

## Running Any Exercise

Every exercise follows the same three-terminal pattern:

**Terminal 1 — Start the Temporal development server:**
```bash
temporal server start-dev
```

**Terminal 2 — Start the worker (inside the exercise folder):**
```bash
source ocr_env/bin/activate
cd <ExerciseFolder>
python worker.py
```

**Terminal 3 — Submit a job:**
```bash
source ocr_env/bin/activate
cd <ExerciseFolder>
python submit_job.py
```

The Temporal Web UI is available at [http://localhost:8233](http://localhost:8233) to inspect workflow runs, history, and replays.

---

## Exercises

### Exercise 1 — Hello World (`HelloWorld_Ex_1`)

**Concept:** The bare minimum Temporal program.

- Define a workflow with `@workflow.defn` and `@workflow.run`
- Define an activity with `@activity.defn`
- Start a worker that registers both
- Submit a workflow from a client

**Key takeaway:** A workflow never calls external code directly — it calls activities via `workflow.execute_activity()`.

---

### Exercise 2 — Structured Data (`Structured_Data_Ex_2`)

**Concept:** Passing structured inputs and outputs using Python dataclasses.

- Define `ImageInput` and `ImageOutput` as `@dataclass`
- Temporal serializes/deserializes them automatically via JSON
- Activities receive and return typed objects

**Key takeaway:** Use dataclasses (or Pydantic models) for all workflow/activity inputs and outputs — never raw dicts.

---

### Exercise 3 — Retry Policies & Timeouts (`Retry_Timeout_Ex_3`)

**Concept:** Making workflows resilient to transient failures.

- `start_to_close_timeout` — max time for a single activity attempt
- `schedule_to_close_timeout` — max time for all attempts combined
- `RetryPolicy` — configure initial interval, backoff coefficient, max interval, and max attempts

```python
RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,      # 1s → 2s → 4s → 8s...
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=5,
)
```

**Key takeaway:** Temporal retries are automatic. You configure the policy — Temporal handles the rest, including crash recovery.

---

### Exercise 4 — Multi-Page Parallel OCR (`MultiPage_OCR_Ex_4`)

**Concept:** Running multiple activities in parallel inside one workflow.

- Accept a list of file paths (`MultiPageInput`)
- Fan out one activity per page using a list comprehension
- `await asyncio.gather(*tasks)` fires all pages simultaneously
- Collect results and handle per-page failures gracefully

**Key takeaway:** `asyncio.gather` inside a workflow runs activities in parallel. Each activity still has its own independent retry policy.

---

### Exercise 5 — Child Workflows (`Child_Workflows_Ex_5`)

**Concept:** Breaking a large workflow into parent + child workflows.

- `PageWorkflow` handles exactly one page — has its own event history and retry budget
- `OCRWorkflow` (parent) spawns one `PageWorkflow` per page via `workflow.execute_child_workflow()`
- Each child gets a unique workflow ID: `{job_id}_page_{n}`

**When to use child workflows vs parallel activities:**

| | Parallel Activities | Child Workflows |
|---|---|---|
| Event history | Shared with parent | Independent per child |
| Max history size | Can hit limits on large jobs | Each child has its own limit |
| Visibility in UI | Single workflow | One entry per child |
| Use case | Short, many tasks | Long-running or complex subtasks |

**Key takeaway:** Child workflows are useful when each unit of work is complex enough to deserve its own event history and lifecycle.

---

### Exercise 6 — Signals & Queries (`Workflow_Signals_Ex_6`)

**Concept:** Communicating with a running workflow from the outside.

- `@workflow.signal` — sends a message *into* the workflow to change state (e.g. cancel)
- `@workflow.query` — reads the current state of the workflow without modifying it

```python
# Send a cancel signal
await handle.signal(OCRWorkflow.cancel_job)

# Query current progress
status = await handle.query(OCRWorkflow.get_status)
```

The workflow checks a `_cancelled` flag between pages and stops gracefully if set.

**Key takeaway:** Signals and queries allow real-time control and introspection of long-running workflows — no polling a database needed.

---

### Exercise 7 — External Service Integration (`External_Service_Ex_7`)

**Concept:** Calling an external HTTP service (NVIDIA Triton Inference Server) from an activity.

- A mock Triton server (`mock_triton.py`) is started with `aiohttp`
- The activity calls it using `httpx` (async HTTP client)
- `ApplicationError` is raised on non-retryable failures
- Retry policy handles transient 503 errors from the server

**Files:**
- `mock_triton.py` — fake Triton server for local testing
- `activity.py` — makes HTTP POST to Triton, parses response
- `workflow.py` — orchestrates pages with cancel support (carries forward from Ex 6)

**Key takeaway:** Activities are the right place for all external I/O. Temporal's retry policy handles transient failures from external services automatically.

---

## Dependencies

```
temporalio==1.28.0   # Temporal Python SDK
aiohttp==3.14.0      # Async HTTP server (mock Triton in Ex 7)
httpx==0.28.1        # Async HTTP client (calling Triton in Ex 7)
pydantic==2.13.4     # Data validation (upcoming exercise)
```

Install: `pip install -r requirements.txt`

---

## Further Reading

- [Temporal Python SDK Docs](https://docs.temporal.io/develop/python)
- [Temporal Web UI](http://localhost:8233) (when dev server is running)
- [Temporal Concepts](https://docs.temporal.io/temporal)
