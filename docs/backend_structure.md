backend/
├── main.py
├── lifespan.py
├── prestart.sh
├── Dockerfile
├── pyproject.toml
├── alembic.ini

├── alembic/
│   ├── env.py                 
│   ├── script.py.mako         
│   └── versions/              
│       ├── __init__.py
│       ├── 0001_init_core_tables.py  
│       ├── 0002_vector_support.py    
│       └── 0003_agent_memory.py    

├── config/
│   ├── __init__.py
│   ├── gateway_settings.py
│   ├── feature_flags.py
│   └── rollout.py

├── health/
│   ├── __init__.py
│   ├── checks.py
│   ├── db.py
│   ├── redis.py
│   ├── vector.py
│   └── llm.py

├── tracing/
│   ├── __init__.py
│   ├── context.py
│   ├── propagation.py
│   ├── middleware.py
│   └── exporters.py

├── resilience/
│   ├── __init__.py
│   ├── circuit_breaker.py
│   ├── retry_policy.py
│   ├── rate_limit_policy.py
│   └── fallback.py

├── policy/
│   ├── __init__.py
│   ├── execution_policy.py
│   ├── cost_policy.py
│   ├── confidence_policy.py
│   ├── escalation_policy.py
│   ├── delegation_policy.py
│   └── kill_switch.py

├── evaluation/
│   ├── __init__.py
│   ├── metrics.py
│   ├── scoring.py
│   ├── feedback.py
│   └── benchmarks.py

├── decisions/
│   ├── __init__.py
│   ├── proposal.py
│   ├── verdict.py
│   └── record.py

├── gateway/
│   ├── __init__.py
│   ├── app.py
│   ├── routes.py
│   ├── dependencies.py
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py
│       ├── rate_limit.py
│       └── tracing.py

├── worker/
│   ├── __init__.py
│   ├── app.py
│   ├── bootstrap.py
│   └── registry.py

├── common/
│   ├── __init__.py

│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logging.py

│   ├── agent_sdk/
│   │   ├── __init__.py
│   │   ├── orchestration_state.py
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── verifier.py
│   │   ├── delegation.py
│   │   ├── lifecycle.py
│   │   ├── registry.py
│   │   └── base_agent.py

│   ├── ai_sdk/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── routing.py
│   │   ├── prompts.py
│   │   ├── tokenization.py
│   │   ├── exceptions.py
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── openai.py
│   │       ├── openrouter.py
│   │       └── gemini.py

│   ├── runtime_agents/
│   │   ├── __init__.py
│   │   ├── tool_manifests.py
│   │   ├── permissions.py
│   │   └── registry.py

│   ├── data_sdk/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── transformation.py
│   │   ├── enrichment.py
│   │   └── export.py

│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── engine.py
│   │   ├── session.py
│   │   ├── migrations.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── meeting.py
│   │       ├── insight.py
│   │       ├── study.py
│   │       └── chat.py

│   ├── messaging/
│   │   ├── __init__.py
│   │   ├── broker.py
│   │   ├── publisher.py
│   │   ├── consumer.py
│   │   └── schemas.py

│   ├── memory/
│   │   ├── __init__.py
│   │   ├── short_term.py
│   │   ├── long_term.py
│   │   ├── episodic.py
│   │   ├── semantic.py
│   │   ├── compressor.py
│   │   └── facade.py

│   ├── vector/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── indexing.py
│   │   ├── search.py
│   │   └── ranking.py

│   └── schemas/
│       ├── __init__.py
│       ├── base.py
│       ├── api_response.py
│       ├── internal.py
│       └── errors.py

├── lobes/
│   ├── insightmate/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── tasks.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── routes.py
│   │   │       └── schemas.py
│   │   └── agent_sdk/
│   │       ├── __init__.py
│   │       ├── core/
│   │       │   ├── planner.py
│   │       │   ├── executor.py
│   │       │   └── verifier.py
│   │       ├── state.py
│   │       ├── constraints.py
│   │       └── registry.py

│   ├── studyflow/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── tasks.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── routes.py
│   │   │       └── schemas.py
│   │   └── agent_sdk/
│   │       ├── __init__.py
│   │       ├── core/
│   │       │   ├── planner.py
│   │       │   ├── tutor.py
│   │       │   └── evaluator.py
│   │       ├── state.py
│   │       ├── constraints.py
│   │       └── registry.py

│   ├── chatbuddy/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── tasks.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── routes.py
│   │   │       └── schemas.py
│   │   └── agent_sdk/
│   │       ├── __init__.py
│   │       ├── core/
│   │       │   ├── conversational.py
│   │       │   ├── emotional.py
│   │       │   └── memory.py
│   │       ├── state.py
│   │       ├── constraints.py
│   │       └── registry.py

│   └── autoagent_hub/
│       ├── __init__.py
│       ├── app.py
│       ├── tasks.py
│       ├── orchestration/
│       │   ├── planner.py
│       │   ├── executor.py
│       │   └── supervisor.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── routes.py
│       │       └── schemas.py
│       └── agent_sdk/
│           ├── __init__.py
│           ├── core/
│           │   ├── coordinator.py
│           │   ├── delegator.py
│           │   └── verifier.py
│           ├── state.py
│           ├── constraints.py
│           └── registry.py

├── scripts/
│   ├── ops/
│   │   ├── migrate.py
│   │   ├── maintenance.py
│   │   └── backfill.py
│   └── dev/
│       ├── seed_data.py
│       └── cli.py
