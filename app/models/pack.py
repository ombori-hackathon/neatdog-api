from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Pack(Base):
    __tablename__ = "packs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("PackMember", back_populates="pack", cascade="all, delete-orphan")
    invitations = relationship("PackInvitation", back_populates="pack", cascade="all, delete-orphan")
    dog = relationship("Dog", back_populates="pack", uselist=False, cascade="all, delete-orphan")
    activity_types = relationship("ActivityType", back_populates="pack", cascade="all, delete-orphan")
