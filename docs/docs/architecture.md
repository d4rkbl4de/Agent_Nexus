# 🧠 Agent Nexus: Canonical Architecture

## I. System Philosophy
Agent Nexus is a **Multi-Lobe Agentic System** designed for high-autonomy tasks. 
- **Lobe Isolation**: Lobes must never import from each other.
- **Shared SDK**: All cross-cutting concerns (DB, LLM, Memory) live in `common/`.
- **Contract Supremacy**: All data crossing the Backend/Frontend boundary must be Zod/Pydantic validated.

## II. Lobe Inventory
1. **AutoAgent_Hub**: The Executive Orchestrator (HMAS logic).
2. **InsightMate**: RAG & Document Analysis.
3. **StudyFlow**: Adaptive Learning & Quiz Generation.
4. **ChatBuddyPlus**: Conversational Memory & State.

## III. Infrastructure (The "Command Center")
- **Database**: Postgres (Relational State)
- **Vector Store**: Qdrant (Long-term Memory)
- **Message Broker**: Redis/Dramatiq (Async Tasks)
- **Orchestrator**: Docker Compose (System-wide lifecycle)