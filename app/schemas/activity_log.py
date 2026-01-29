from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.activity_type import ActivityType
from app.schemas.user import User


class ActivityLogCreate(BaseModel):
    """Schema for creating an activity log entry."""

    activity_type_id: int
    notes: str | None = None
    logged_at: datetime | None = Field(default_factory=datetime.utcnow)


class ActivityLog(BaseModel):
    """Schema for activity log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pack_id: int
    dog_id: int
    activity_type_id: int
    user_id: int
    notes: str | None
    logged_at: datetime
    created_at: datetime


class ActivityLogWithDetails(BaseModel):
    """Schema for activity log response with related details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pack_id: int
    dog_id: int
    activity_type_id: int
    user_id: int
    notes: str | None
    logged_at: datetime
    created_at: datetime
    activity_type: ActivityType
    user: User
