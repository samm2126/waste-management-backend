from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), nullable=False, default="citizen")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    waste_reports = relationship("WasteReport", back_populates="user")
    collection_requests = relationship("CollectionRequest", back_populates="user")
    complaints = relationship("Complaint", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    collector_profile = relationship("CollectorProfile", back_populates="user", uselist=False)
    assigned_collections = relationship(
        "CollectionRequest",
        foreign_keys="CollectionRequest.assigned_collector_id",
        back_populates="assigned_collector",
    )
    collector_assignments = relationship(
        "CollectorAssignment",
        foreign_keys="CollectorAssignment.collector_id",
        back_populates="collector",
    )
