from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.database import Base


class WasteCategory(Base):
    __tablename__ = "waste_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    is_recyclable = Column(Boolean, default=False)
    is_organic = Column(Boolean, default=False)
    is_hazardous = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    waste_reports = relationship("WasteReport", back_populates="category")
    collection_requests = relationship("CollectionRequest", back_populates="category")
    recycling_center_categories = relationship("RecyclingCenterCategory", back_populates="category")
