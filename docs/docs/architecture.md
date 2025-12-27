# AGENT NEXUS ARCHITECTURE SPECIFICATION

## I. SYSTEM TOPOLOGY



### 1. Control Plane (The Sovereign)
* **Gateway:** FastAPI-driven entry point using versioned `/v1/` routes. Enforces **Rule 18** (Translation Layers).
* **Policy Engine:** Root-level enforcement of budgets, safety, and delegation. **Rule 3** (Policy Beats Intelligence).
* **Decision Hub:** Asynchronous audit trail for every agent proposal via `decisions/record.py`.
* **Worker Mesh:** Distributed task execution via Celery/RabbitMQ. Enforces **Rule 11** (Replaceable Workers).

### 2. Cognition Layer (The Lobes)
* **Isolation:** Each Lobe (`InsightMate`, `StudyFlow`, etc.) is a bounded context. **Rule 6** (Product-Bounded).
* **SDK-Only Reasoning:** All logic resides in `lobes/*/agent_sdk/core/`. **Rule 8** (Reasoning Isolation).
* **Statelessness:** Context is restored per-turn from the Memory Facade. **Rule 9** (Statelessness).

### 3. Data & Memory SDK (The Continuity)
* **Memory Tiers:** * **Short-Term:** Redis-backed ephemeral state.
    * **Long-Term:** PostgreSQL/Vector-backed episodic/semantic retrieval.
* **Facade Access:** Direct DB/Vector imports are strictly prohibited. **Rule 15** and **Rule 16**.

---

## II. EXECUTION FLOW

### 1. The Decision Cycle
1.  **Request:** Gateway receives intent and generates a `trace_id`.
2.  **Proposal:** Agent SDK generates an `ActionProposal` based on user intent.
3.  **Verdict:** Root `policy/` engine validates the proposal against cost/safety.
4.  **Execution:** If approved, `worker/` invokes the SDK to perform the action.
5.  **Record:** Results are logged in `decisions/record.py` for retrospection.



### 2. Resilience Strategy
* **Circuit Breakers:** Wrapped around all LLM and Provider calls.
* **Kill Switch:** Global halt capability via `policy/kill_switch.py`.
* **Escalation:** Explicit hand-off to human or supervisor when confidence < threshold.

---

## III. FRONTEND-BACKEND CONTRACTS

### 1. Schema Integrity
* **Zod Validation:** Every Backend response must match a Frontend Zod schema.
* **Silent Failure Prevention:** UI must fail loudly if data violates the contract.

### 2. Agentic UI Patterns
* **Streaming:** Thought-streams and tool-execution visualizers are first-class components.
* **Atomic Updates:** High-frequency agent data uses atomic state selectors to prevent UI lag.

---

## IV. ABSOLUTE CONSTRAINTS

| Constraint | Enforcement Mechanism |
| :--- | :--- |
| **No Reasoning in Tasks** | Code Linting / Rule 10 |
| **No Direct DB Access** | Data Facade / Rule 2 |
| **No Cross-Lobe Imports** | Module Isolation / Rule 6 |
| **No Unrecorded Actions** | Decision Record / Rule 20 |


