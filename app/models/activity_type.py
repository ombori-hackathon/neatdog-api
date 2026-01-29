from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class ActivityType(Base):
    __tablename__ = "activity_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False)  # SF Symbol name
    color = Column(String, nullable=False)  # hex color
    pack_id = Column(Integer, ForeignKey("packs.id"), nullable=True)  # null for default types
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    pack = relationship("Pack", back_populates="activity_types")

    # Unique constraint on (name, pack_id) for custom types
    __table_args__ = (
        UniqueConstraint("name", "pack_id", name="uq_activity_type_name_pack"),
    )
