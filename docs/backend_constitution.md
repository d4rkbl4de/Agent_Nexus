# 📜 AGENT NEXUS BACKEND CONSTITUTION

---

## I. CORE PHILOSOPHY (FOUNDATIONAL LAWS)

### Rule 1 — The Backend Is an Agent Platform, Not an App

This system exists to **host, orchestrate, and evolve agents**.
Everything else (APIs, UIs, tasks) is support infrastructure.

If a feature does not:
• improve agent reasoning
• improve agent autonomy
• improve agent reliability

…it does not belong in core logic.

---

### Rule 2 — Agents Do Not Own Infrastructure

Agents:
• do not talk directly to databases
• do not talk directly to Redis
• do not talk directly to vector stores
• do not call LLM providers directly

Agents ask **SDKs**. SDKs talk to infrastructure.

Violation = architectural failure.

---

### Rule 3 — Policy Always Beats Intelligence

Agents may **propose** actions.
Policies **decide** whether actions are allowed.

Agents never:
• enforce budgets
• enforce retries
• enforce escalation
• enforce safety limits

If an agent enforces a policy, the design is wrong.

---

## II. DIRECTORY OWNERSHIP RULES

### Rule 4 — Root-Level Modules Are Control Plane Only

At root level (`gateway/`, `worker/`, `policy/`, `resilience/`, `tracing/`):

Allowed:
• orchestration
• routing
• enforcement
• lifecycle management

Forbidden:
• domain logic
• reasoning logic
• agent behavior

Root code coordinates. It never “thinks”.

---

### Rule 5 — `common/` Is a Shared SDK, Not a Dumping Ground

`common/` may contain:
• abstractions
• primitives
• shared contracts
• infrastructure adapters

`common/` may NOT contain:
• product-specific logic
• lobe-specific assumptions
• feature experiments

If it only serves one lobe, it does not belong in `common/`.

---

### Rule 6 — Lobes Are Product-Bounded Contexts

Each lobe:
• owns its API surface
• owns its tasks
• owns its agent extensions

A lobe must be removable without breaking other lobes.

If removing a lobe breaks another lobe → coupling violation.

---

## III. AGENT RULES (CRITICAL)

### Rule 7 — One Brain Per Agent

An agent has:
• one planner
• one executor
• one verifier

There must never be:
• duplicate reasoning paths
• parallel “helper agents” inside a lobe

Multiple brains = undefined behavior.

---

### Rule 8 — Agent SDK Is the Only Place for Reasoning

Reasoning logic may exist ONLY in:
• `common.agent_sdk`
• `lobes/*/agent_sdk`

Forbidden locations:
• `tasks.py`
• `services/`
• `api/routes.py`
• `utils.py`

If reasoning leaks into those, the agent becomes untestable.

---

### Rule 9 — Agents Are Stateless Between Turns

Agents:
• may read memory
• may write memory
• may update state objects

Agents must never:
• store state in globals
• rely on process memory
• assume task locality

All continuity flows through explicit state.

---

## IV. TASK & WORKER RULES

### Rule 10 — Tasks Execute, They Do Not Decide

`tasks.py`:
• schedules work
• invokes agents
• handles retries

Tasks must never:
• reason
• branch on meaning
• interpret user intent

If a task makes a “decision”, it belongs in an agent.

---

### Rule 11 — Workers Are Replaceable

Any worker must be killable at any moment.

Therefore:
• no in-memory assumptions
• no cached decisions
• no orphan state

If a worker restart breaks logic, the design is invalid.

---

## V. POLICY & RESILIENCE RULES

### Rule 12 — No Direct Retries Without Circuit Breakers

Every retry must:
• be governed by policy
• respect circuit breakers
• emit trace data

Blind retries are forbidden.
They amplify outages.

---

### Rule 13 — Cost Is a First-Class Constraint

Every LLM call must:
• report estimated cost
• report token usage
• pass through cost policy

If cost cannot be measured, the call is illegal.

---

### Rule 14 — Escalation Is Explicit

Agents never “panic”.

Escalation paths must be:
• declared
• policy-driven
• observable

Implicit escalation = silent failure.

---

## VI. MEMORY & DATA RULES

### Rule 15 — Memory Has Types

Memory is not a blob.

You must always know:
• short-term vs long-term
• episodic vs semantic
• private vs shared

Mixing memory types leads to hallucination and drift.

---

### Rule 16 — Memory Writes Are Intentional

Agents must never:
• auto-persist everything
• log raw thoughts blindly

Memory is curated, not recorded.

---

### Rule 17 — Vector Search Is Advisory

Vector results:
• inform agents
• never override reasoning

Agents decide relevance. Vectors suggest.

---

## VII. API & SCHEMA RULES

### Rule 18 — APIs Are Translation Layers

API schemas:
• are not internal models
• are not DB models
• are not agent state

APIs translate external intent into internal contracts.

---

### Rule 19 — Version APIs Early

Every public API must:
• live under `/v1/`
• assume `/v2/` will exist

Unversioned APIs are technical debt.

---

## VIII. OBSERVABILITY & DEBUGGING RULES

### Rule 20 — No Execution Without Trace Context

Every request must carry:
• trace_id
• agent_id (if applicable)
• task_id

If it cannot be traced, it does not run.

---

### Rule 21 — Logs Must Be Structured

Logs must be:
• machine-readable
• trace-linked
• policy-aware

Human-only logs do not scale.

---

## IX. SCALING & EVOLUTION RULES

### Rule 22 — Adding an Agent Must Not Require Refactoring

A new agent should require:
• new lobe OR
• new agent_sdk module

If adding an agent forces refactors elsewhere, abstraction failed.

---

### Rule 23 — Experimental Logic Is Isolated

Experiments go:
• behind feature flags
• inside lobe boundaries

No experiments in `common/`.

---

### Rule 24 — Monolith First, Services Later

This backend is:
• intentionally monolithic
• intentionally modular

Extraction into services must be:
• optional
• mechanical
• low-risk

Premature microservices are forbidden.

---

## X. ABSOLUTE PROHIBITIONS

These are hard “no”s.

❌ Agents importing providers directly
❌ Agents importing DB models
❌ Tasks reasoning
❌ Policies embedded in agents
❌ Memory accessed without facade
❌ Cross-lobe imports
❌ Silent retries
❌ Global state

---

