import asyncio
import os
import time
from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from common.config.logging import logger

class MaintenanceManager:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_key = os.getenv("QDRANT_API_KEY")
        self.engine = create_async_engine(self.db_url)
        self.vector_client = AsyncQdrantClient(url=self.qdrant_url, api_key=self.qdrant_key)

    async def vacuum_postgres(self):
        try:
            async with self.engine.connect() as conn:
                await conn.execution_options(isolation_level="AUTOCOMMIT").execute(text("VACUUM ANALYZE"))
            logger.info("MAINTENANCE_PG_VACUUM_SUCCESS")
        except Exception as e:
            logger.error(f"MAINTENANCE_PG_VACUUM_FAILED | Error: {str(e)}")

    async def prune_stale_vectors(self, collection_name: str, days: int = 90):
        try:
            threshold_timestamp = int(time.time()) - (days * 86400)
            
            await self.vector_client.delete(
                collection_name=collection_name,
                points_selector=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="created_at",
                            range=models.Range(lt=threshold_timestamp)
                        )
                    ]
                )
            )
            logger.info(f"MAINTENANCE_VECTOR_PRUNE_SUCCESS | Collection: {collection_name} | Days: {days}")
        except Exception as e:
            logger.error(f"MAINTENANCE_VECTOR_PRUNE_FAILED | Collection: {collection_name} | Error: {str(e)}")

    async def optimize_vector_collections(self):
        try:
            collections = await self.vector_client.get_collections()
            for col in collections.collections:
                await self.vector_client.update_collection(
                    collection_name=col.name,
                    optimizer_config=models.OptimizersConfigDiff(indexing_threshold=10000)
                )
            logger.info("MAINTENANCE_VECTOR_OPTIMIZATION_SUCCESS")
        except Exception as e:
            logger.error(f"MAINTENANCE_VECTOR_OPTIMIZATION_FAILED | Error: {str(e)}")

    async def run_all(self):
        logger.info("MAINTENANCE_CYCLE_START")
        await self.vacuum_postgres()
        
        target_collections = ["memories", "insights"]
        for col in target_collections:
            await self.prune_stale_vectors(col)
            
        await self.optimize_vector_collections()
        logger.info("MAINTENANCE_CYCLE_COMPLETE")
        await self.engine.dispose()
        await self.vector_client.close()

if __name__ == "__main__":
    manager = MaintenanceManager()
    asyncio.run(manager.run_all())