## I. CORE PHILOSOPHY (FRONTEND FOUNDATIONAL LAWS)

### Frontend Rule 1 — The Frontend Is an Agent Interface, Not an App

The frontend exists to:
• observe agents
• command agents
• visualize agent state
• enforce user-facing policy boundaries

It does **not**:
• contain domain intelligence
• contain decision logic
• contain fallback reasoning

If the frontend “decides” instead of **displaying or dispatching**, it violates the platform.

---

### Frontend Rule 2 — UI Never Thinks

Frontend code must never:
• infer intent
• reinterpret agent output
• apply “smart defaults” that change meaning
• branch on semantic meaning

If meaning is interpreted, it belongs to:
• backend policy
• backend agent
• backend SDK

UI renders **facts**, not conclusions.

---

## II. DIRECTORY OWNERSHIP & STRUCTURE RULES

### Frontend Rule 3 — `app/` Is Routing Only (Hard Law)

`src/app/` may contain:
• layouts
• route segments
• loading/error boundaries

It may **not** contain:
• business logic
• state derivation
• agent interaction logic
• policy checks

If a route imports anything other than:
• layout components
• page shells
• contract types

— it is illegal.

---

### Frontend Rule 4 — Lobes Mirror Backend Lobes One-to-One

Each frontend lobe:
• maps exactly to one backend lobe
• owns its UI, state, and contracts
• can be deleted without breaking others

No “shared feature UI” across lobes unless it lives in **core**.

Violation = coupling.

---

### Frontend Rule 5 — No Cross-Lobe Imports (Absolute)

A frontend lobe must **never** import:
• another lobe’s components
• another lobe’s state
• another lobe’s hooks

Cross-lobe communication happens **only** through:
• core mediator
• event bus
• backend APIs

Same law as backend. No exceptions.

---

## III. STATE & DATA FLOW RULES (CRITICAL)

### Frontend Rule 6 — State Is Derived, Not Invented

Frontend state must be:
• a projection of backend state
• explicitly derived
• traceable to a response or event

Frontend must never:
• synthesize agent state
• cache decisions
• “correct” agent outputs

If frontend state cannot be explained by a backend source, it is illegal.

---

### Frontend Rule 7 — No Hidden State

Forbidden:
• module-level state
• implicit closures
• singleton mutation
• React context storing agent state without IDs

All state must be:
• scoped
• keyed
• resettable
• replayable

Frontend must tolerate refresh, reload, tab death.

---

### Frontend Rule 8 — Event-Driven, Never Imperative

Frontend actions:
• emit events
• dispatch commands
• subscribe to streams

They must never:
• call multiple APIs conditionally
• “fix” failed workflows
• retry silently

Retry logic is backend policy territory.

---

## IV. AGENT INTERACTION RULES

### Frontend Rule 9 — Agents Are Black Boxes

Frontend must treat agents as:
• opaque
• non-deterministic
• policy-governed

Frontend must never:
• assume agent step order
• assume agent completion time
• assume agent correctness

The UI reflects uncertainty explicitly.

---

### Frontend Rule 10 — One Command, One Intent

Each user action must map to:
• one command
• one backend intent
• one trace ID

Never bundle multiple semantic actions into one UI event.

If a button does more than one thing conceptually, the design is wrong.

---

### Frontend Rule 11 — No Agent Simulation

Frontend must never:
• simulate agent thinking
• predict agent outcomes
• pre-emptively block actions “because agent might fail”

That logic belongs to policy.

---

## V. POLICY & SAFETY MIRRORING

### Frontend Rule 12 — Policy Is Displayed, Not Enforced

Frontend may:
• display policy constraints
• show limits
• show cost warnings

Frontend must never:
• enforce budgets
• enforce retries
• enforce safety logic
• enforce escalation rules

UI may *warn*. Backend *decides*.

---

### Frontend Rule 13 — Cost Is Visible Everywhere

If an action costs tokens, money, or time:
• it must be visible
• it must be attributed
• it must be traceable

Hidden cost = trust failure.

---

## VI. SCHEMAS, CONTRACTS & TYPES

### Frontend Rule 14 — Contracts Are Border Control

Frontend must consume:
• explicit schemas
• versioned contracts
• validated responses

Frontend must never:
• rely on inferred shapes
• destructure “unknown” payloads
• tolerate silent schema drift

If schema changes, frontend should **break loudly**.

---

### Frontend Rule 15 — No Backend Model Leakage

Frontend must never import:
• DB models
• internal agent state
• internal policy enums

Only API contracts cross the boundary.

Same rule as backend Rule 18.

---

## VII. OBSERVABILITY & TRACEABILITY

### Frontend Rule 16 — Every Action Emits Trace Context

Every frontend command must include:
• trace_id
• user_id
• session_id
• optional agent_id

If an action cannot be traced end-to-end, it must not exist.

---

### Frontend Rule 17 — Logs Are Structured, Not Console Spam

Forbidden:
• console.log debugging
• human-only logs

Allowed:
• structured telemetry
• trace-linked logs
• policy-aware event records

Frontend is part of the observability chain.

---

## VIII. UI COMPONENT RULES

### Frontend Rule 18 — Components Are Dumb by Default

Components should:
• render props
• emit events
• stay pure

Forbidden:
• embedded side effects
• hidden async calls
• business logic inside JSX

Logic lives in hooks or core.

---

### Frontend Rule 19 — Hooks Are the Only Stateful Abstraction

Stateful logic must live in:
• hooks
• stores
• mediators

Never inside:
• components
• layouts
• pages

Hooks are the frontend equivalent of SDKs.

---

## IX. SCALING & EVOLUTION

### Frontend Rule 20 — Adding a Lobe Requires Zero Refactors

A new frontend lobe must:
• plug into routing
• register with mediator
• define its contracts

No existing lobe should change.

If it does, abstraction failed.

---

### Frontend Rule 21 — Experimental UI Is Isolated

Experiments:
• live behind flags
• stay inside lobes
• never leak to core

Same law as backend Rule 23.

---

## X. ABSOLUTE PROHIBITIONS (FRONTEND)

Hard “no” list:

❌ Cross-lobe imports
❌ Semantic branching in UI
❌ Agent simulation
❌ Policy enforcement in frontend
❌ Hidden retries
❌ Global mutable state
❌ Schema inference
❌ Cost-blind UI actions

Violating any of these means the frontend is no longer compatible with your backend constitution.




