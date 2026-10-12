from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.app.database import Base


class CollectorProfile(Base):
    __tablename__ = "collector_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    specialization = Column(String(255), nullable=False, default="General waste collection")
    vehicle_type = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    rating = Column(Integer, default=0)
    total_collections = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="collector_profile")


class CollectorAssignment(Base):
    __tablename__ = "collector_assignments"
    __table_args__ = (
        UniqueConstraint("collection_request_id", "collector_id", name="uq_collection_collector"),
    )

    id = Column(Integer, primary_key=True, index=True)
    collection_request_id = Column(Integer, ForeignKey("collection_requests.id"), nullable=False)
    collector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False, default="assigned")
    notes = Column(String(500), nullable=True)

    collection_request = relationship("CollectionRequest", back_populates="assignments")
    collector = relationship("User", foreign_keys=[collector_id], back_populates="collector_assignments")
