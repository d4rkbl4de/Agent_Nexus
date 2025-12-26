import asyncio
import os
import sys
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from common.config.logging import logger

class MigrationManager:
    def __init__(self):
        self.pg_url = os.getenv("DATABASE_URL")
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_key = os.getenv("QDRANT_API_KEY")
        
        if not self.pg_url:
            logger.critical("MIGRATION_FAILED | DATABASE_URL_MISSING")
            sys.exit(1)

    async def migrate_postgres(self):
        engine = create_async_engine(self.pg_url)
        try:
            async with engine.begin() as conn:
                logger.info("PG_MIGRATION_START | Checking schema integrity")
                # Core extensions required for Agentic operations
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";"))
                
                # Validation query to ensure connection is healthy
                await conn.execute(text("SELECT 1"))
                logger.info("PG_MIGRATION_SUCCESS")
        except Exception as e:
            logger.error(f"PG_MIGRATION_FAILED | Error: {str(e)}")
            raise
        finally:
            await engine.dispose()

    async def migrate_vector_storage(self):
        client = AsyncQdrantClient(url=self.qdrant_url, api_key=self.qdrant_key)
        collections = {
            "memories": 1536,  # OpenAI text-embedding-3-small
            "insights": 1536,
            "tasks_archive": 1536
        }
        
        try:
            existing = await client.get_collections()
            existing_names = [c.name for c in existing.collections]
            
            for name, size in collections.items():
                if name not in existing_names:
                    await client.create_collection(
                        collection_name=name,
                        vectors_config=models.VectorParams(
                            size=size,
                            distance=models.Distance.COSINE
                        ),
                        optimizers_config=models.OptimizersConfigDiff(memmap_threshold=20000)
                    )
                    logger.info(f"VECTOR_COLLECTION_CREATED | Name: {name}")
                else:
                    logger.info(f"VECTOR_COLLECTION_EXISTS | Name: {name}")
            
            logger.info("VECTOR_MIGRATION_SUCCESS")
        except Exception as e:
            logger.error(f"VECTOR_MIGRATION_FAILED | Error: {str(e)}")
            raise
        finally:
            await client.close()

    async def execute_all(self):
        logger.info("GLOBAL_MIGRATION_INITIATED")
        try:
            await self.migrate_postgres()
            await self.migrate_vector_storage()
            logger.info("GLOBAL_MIGRATION_COMPLETE")
        except Exception as e:
            logger.critical(f"GLOBAL_MIGRATION_HALTED | {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    manager = MigrationManager()
    asyncio.run(manager.execute_all())