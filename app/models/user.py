# User model
from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    hashed_password=Column(String,nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))