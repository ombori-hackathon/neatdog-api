from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.user import User


class PackCreate(BaseModel):
    name: str


class Pack(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class PackMemberSchema(BaseModel):
    id: int
    user_id: int
    role: str
    joined_at: datetime
    user: User

    class Config:
        from_attributes = True


class PackWithMembers(Pack):
    members: list[PackMemberSchema] = []

    class Config:
        from_attributes = True


class PackInvitationCreate(BaseModel):
    email: EmailStr


class PackInvitation(BaseModel):
    id: int
    email: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AcceptInvitation(BaseModel):
    token: str
