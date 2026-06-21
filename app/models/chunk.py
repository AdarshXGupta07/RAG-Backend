from sqlalchemy import Column, Integer, Text, ForeignKey
from app.database import Base
from pgvector.sqlalchemy import Vector
class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    content = Column(Text, nullable=False)

    chunk_index = Column(Integer)

    document_id = Column(Integer, ForeignKey("documents.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    embedding=Column(Vector(1024),nullable=True)