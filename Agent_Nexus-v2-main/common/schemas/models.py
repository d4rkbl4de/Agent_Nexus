from sqlalchemy import Column, Integer, String, DateTime, func, Text, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Lobe(Base):
    __tablename__ = "lobes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    api_endpoint = Column(String)
    
    memories = relationship("Memory", back_populates="lobe")
    
    def __repr__(self):
        return f"<Lobe(name='{self.name}')>"

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    lobe_id = Column(Integer, ForeignKey('lobes.id'), index=True)
    
    key = Column(String, index=True)
    value_json = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    lobe = relationship("Lobe", back_populates="memories")
    actions = relationship("ActionItem", back_populates="source_memory")
    
    def __repr__(self):
        return f"<Memory(user_id='{self.user_id}', key='{self.key}')>"

class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey('memories.id'), index=True, nullable=False)
    
    description = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False) # pending, complete, blocked
    due_date = Column(DateTime(timezone=True), nullable=True)
    is_urgent = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    source_memory = relationship("Memory", back_populates="actions")

    def __repr__(self):
        return f"<ActionItem(status='{self.status}', description='{self.description[:30]}...')>"