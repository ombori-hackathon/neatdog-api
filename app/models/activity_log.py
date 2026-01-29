from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    pack_id = Column(Integer, ForeignKey("packs.id"), nullable=False)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # who logged it
    notes = Column(String, nullable=True)  # optional notes
    logged_at = Column(DateTime, nullable=False)  # when activity occurred
    created_at = Column(
        DateTime, nullable=False, default=datetime.utcnow
    )  # when record was created

    # Relationships
    pack = relationship("Pack")
    dog = relationship("Dog")
    activity_type = relationship("ActivityType")
    user = relationship("User")

    # Index for efficient queries
    __table_args__ = (
        Index("ix_activity_logs_pack_id_logged_at", "pack_id", "logged_at"),
    )
