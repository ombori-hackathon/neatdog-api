from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DogCreate(BaseModel):
    """Schema for creating a dog."""

    name: str
    breed: str | None = None
    birth_date: date | None = None
    photo_url: str | None = None


class DogUpdate(BaseModel):
    """Schema for updating a dog."""

    name: str | None = None
    breed: str | None = None
    birth_date: date | None = None
    photo_url: str | None = None


class Dog(BaseModel):
    """Schema for dog response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pack_id: int
    name: str
    breed: str | None
    birth_date: date | None
    photo_url: str | None
    created_at: datetime
