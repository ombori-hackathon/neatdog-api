from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityTypeCreate(BaseModel):
    """Schema for creating a custom activity type."""

    name: str
    icon: str  # SF Symbol name
    color: str  # hex color


class ActivityType(BaseModel):
    """Schema for activity type response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    icon: str
    color: str
    pack_id: int | None
    is_default: bool
    created_at: datetime
