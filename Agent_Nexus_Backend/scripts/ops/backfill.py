import asyncio
import os
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from common.config.logging import logger
from common.vector.indexing import VectorIndexer

class VectorBackfiller:
    def __init__(self, batch_size: int = 100):
        self.db_url = os.getenv("DATABASE_URL")
        self.batch_size = batch_size
        self.engine = create_async_engine(self.db_url)
        self.indexer_map: Dict[str, VectorIndexer] = {}

    def _get_indexer(self, collection_name: str) -> VectorIndexer:
        if collection_name not in self.indexer_map:
            self.indexer_map[collection_name] = VectorIndexer(collection_name=collection_name)
        return self.indexer_map[collection_name]

    async def backfill_table_to_vector(
        self, 
        table_name: str, 
        collection_name: str, 
        text_column: str, 
        metadata_columns: List[str]
    ):
        trace_id = f"backfill-{uuid.uuid4()}"
        logger.info(f"BACKFILL_START | Table: {table_name} | Collection: {collection_name} | Trace: {trace_id}")
        
        indexer = self._get_indexer(collection_name)
        offset = 0
        
        try:
            while True:
                async with self.engine.connect() as conn:
                    query = text(f"""
                        SELECT id, {text_column}, {', '.join(metadata_columns)} 
                        FROM {table_name} 
                        ORDER BY id 
                        LIMIT :limit OFFSET :offset
                    """)
                    result = await conn.execute(query, {"limit": self.batch_size, "offset": offset})
                    rows = result.fetchall()

                if not rows:
                    break

                texts = [row[1] for row in rows if row[1]]
                metadatas = [
                    {col: getattr(row, col) for col in metadata_columns} 
                    for row in rows if row[1]
                ]
                ids = [str(row[0]) for row in rows if row[1]]

                if texts:
                    success = await indexer.upsert_documents(
                        texts=texts,
                        metadata=metadatas,
                        ids=ids,
                        trace_id=trace_id
                    )
                    
                    if not success:
                        logger.error(f"BACKFILL_BATCH_FAILURE | Table: {table_name} | Offset: {offset}")
                        raise Exception("Batch processing failed")

                logger.info(f"BACKFILL_PROGRESS | Table: {table_name} | Processed: {offset + len(rows)}")
                offset += self.batch_size

            logger.info(f"BACKFILL_COMPLETE | Table: {table_name} | Trace: {trace_id}")
        
        except Exception as e:
            logger.critical(f"BACKFILL_CRITICAL_ERROR | Table: {table_name} | Error: {str(e)}")
            raise
        finally:
            await self.engine.dispose()

    async def run_standard_backfill(self):
        tasks = [
            self.backfill_table_to_vector(
                table_name="meeting_summaries",
                collection_name="insights",
                text_column="summary_text",
                metadata_columns=["user_id", "meeting_id", "created_at"]
            ),
            self.backfill_table_to_vector(
                table_name="study_notes",
                collection_name="knowledge",
                text_column="content",
                metadata_columns=["user_id", "subject", "importance"]
            )
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    backfiller = VectorBackfiller()
    asyncio.run(backfiller.run_standard_backfill())