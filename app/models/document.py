from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="processing")
    file_path = Column(String, nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))