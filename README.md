# Agent Nexus

Agent Nexus is a modular, agentic AI system designed as a long-term automation platform.
It follows strict architectural boundaries to support scalability, reasoning agents,
and independent evolution of frontend and backend systems.

This repository is the **root workspace** that coordinates all major components.

---

## Repository Structure

Agent_Nexus/
├── Agent_Nexus-v2-main/        Backend brain (agents, lobes, shared SDK)
├── agent_nexus_frontend/       Frontend body (Next.js / React)
├── docs/                       Architecture decisions and constitutions
├── scripts/                    Repo-level automation utilities
├── docker-compose.yml          Service orchestration
├── Dockerfile                  Backend image definition
├── README.md                   This file
└── .editorconfig               Formatting standards

---

## Core Principles

- Backend and frontend are **strictly isolated**
- Lobes never import from each other directly
- Cross-lobe communication happens only via the core mediator
- Frontend contains no business logic
- Architecture decisions are documented and treated as immutable

---

## Running the Backend (Development)

Requirements:
- Docker
- Docker Compose

From the repository root:

docker compose up --build

This will start:
- Backend API
- Background workers
- Database
- Vector storage

---

## Frontend Development

The frontend is developed independently inside:

agent_nexus_frontend/

Refer to its own README for setup instructions.
Frontend communicates with backend strictly through API contracts.

---

## Documentation

All architectural decisions, rules, and system constraints are stored in:

docs/

If a rule is not written there, it is not a rule.

---

## Status

This system is under active development.
Stability is prioritized over speed.
Architecture is considered a first-class artifact.
