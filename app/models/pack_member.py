from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class PackMember(Base):
    __tablename__ = "pack_members"

    id = Column(Integer, primary_key=True, index=True)
    pack_id = Column(Integer, ForeignKey("packs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # 'owner', 'admin', 'member'
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Unique constraint on (pack_id, user_id)
    __table_args__ = (UniqueConstraint("pack_id", "user_id", name="uq_pack_member"),)

    # Relationships
    pack = relationship("Pack", back_populates="members")
    user = relationship("User")
