from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.database import Base


class CollectionRequest(Base):
    __tablename__ = "collection_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=False)
    collection_date = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    estimated_weight = Column(Float, default=0.0)
    actual_weight = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("waste_categories.id"), nullable=False)
    assigned_collector_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    waste_report_id = Column(Integer, ForeignKey("waste_reports.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="collection_requests")
    assigned_collector = relationship(
        "User",
        foreign_keys=[assigned_collector_id],
        back_populates="assigned_collections",
    )
    category = relationship("WasteCategory", back_populates="collection_requests")
    waste_report = relationship("WasteReport", back_populates="collection_requests")
    assignments = relationship("CollectorAssignment", back_populates="collection_request")
    feedback = relationship("Feedback", back_populates="collection_request", uselist=False)
