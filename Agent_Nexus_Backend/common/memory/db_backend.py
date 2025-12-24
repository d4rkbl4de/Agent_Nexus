from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import Table, Column, String, DateTime, JSON, MetaData, Text
from .history_model import MemoryRecord


metadata = MetaData()

memory_table = Table(
    "agent_memory",
    metadata,
    Column("id", String, primary_key=True),
    Column("agent_id", String, index=True),
    Column("role", String),
    Column("content", Text),
    Column("metadata", JSON),
    Column("timestamp", DateTime),
)


class DBMemoryBackend:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def add(self, record: MemoryRecord) -> None:
        with self.session_factory() as session:
            session.execute(
                memory_table.insert().values(
                    id=record.id,
                    agent_id=record.agent_id,
                    role=record.role,
                    content=record.content,
                    metadata=record.metadata,
                    timestamp=record.timestamp,
                )
            )
            session.commit()

    def fetch(self, agent_id: str, limit: int | None = None) -> List[MemoryRecord]:
        with self.session_factory() as session:
            query = (
                session.query(memory_table)
                .filter(memory_table.c.agent_id == agent_id)
                .order_by(memory_table.c.timestamp.desc())
            )
            if limit:
                query = query.limit(limit)
            rows = query.all()
            return [
                MemoryRecord(
                    id=row.id,
                    agent_id=row.agent_id,
                    role=row.role,
                    content=row.content,
                    metadata=row.metadata,
                    timestamp=row.timestamp,
                )
                for row in reversed(rows)
            ]

    def clear(self, agent_id: str) -> None:
        with self.session_factory() as session:
            session.execute(
                memory_table.delete().where(memory_table.c.agent_id == agent_id)
            )
            session.commit()
