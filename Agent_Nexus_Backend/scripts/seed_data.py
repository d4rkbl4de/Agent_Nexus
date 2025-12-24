import asyncio
from sqlalchemy import insert
from src.core.db.session import async_session
from src.lobes.autoagent_hub.models import Agent
from src.lobes.chatbuddy.models import Conversation
from src.core.llm.embeddings import embed_text
from src.core.vector.qdrant_client import get_qdrant_client

async def seed_agents():
    async with async_session() as session:
        session.add_all([
            Agent(name="InsightMate", active=True),
            Agent(name="StudyFlow", active=True),
            Agent(name="ChatBuddy", active=True),
            Agent(name="AutoAgent", active=True),
        ])
        await session.commit()

async def seed_vectors():
    client = get_qdrant_client()
    vectors = await embed_text(["system initialized"])
    client.upsert(
        collection_name="system_memory",
        points=[
            {
                "id": 1,
                "vector": vectors[0],
                "payload": {"type": "system"}
            }
        ]
    )

async def main():
    await seed_agents()
    await seed_vectors()

if __name__ == "__main__":
    asyncio.run(main())
