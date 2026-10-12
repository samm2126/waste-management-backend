from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.database import Base


class RecyclingCenter(Base):
    __tablename__ = "recycling_centers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    operating_hours = Column(String(200), nullable=True)
    website = Column(String(255), nullable=True)
    is_active = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    accepted_categories = relationship("RecyclingCenterCategory", back_populates="center")


class RecyclingCenterCategory(Base):
    __tablename__ = "recycling_center_categories"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("recycling_centers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("waste_categories.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    center = relationship("RecyclingCenter", back_populates="accepted_categories")
    category = relationship("WasteCategory", back_populates="recycling_center_categories")
