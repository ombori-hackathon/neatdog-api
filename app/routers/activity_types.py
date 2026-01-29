from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db import get_db
from app.models.activity_type import ActivityType as ActivityTypeModel
from app.models.user import User
from app.routers.packs import verify_pack_member
from app.schemas.activity_type import ActivityType, ActivityTypeCreate

router = APIRouter()


@router.get(
    "/packs/{pack_id}/activity-types",
    response_model=list[ActivityType],
    tags=["activity-types"],
)
async def list_activity_types(
    pack_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all activity types available to a pack.
    Returns default types (is_default=True) + pack's custom types.
    User must be a member of the pack.
    """
    # Verify user is a member of the pack
    await verify_pack_member(pack_id, current_user, db)

    # Get default types (pack_id is None) and custom types for this pack
    activity_types = (
        db.query(ActivityTypeModel)
        .filter(
            or_(
                ActivityTypeModel.is_default.is_(True),
                ActivityTypeModel.pack_id == pack_id,
            )
        )
        .order_by(ActivityTypeModel.is_default.desc(), ActivityTypeModel.name)
        .all()
    )

    return activity_types


@router.post(
    "/packs/{pack_id}/activity-types",
    response_model=ActivityType,
    status_code=status.HTTP_201_CREATED,
    tags=["activity-types"],
)
async def create_activity_type(
    pack_id: int,
    activity_type_data: ActivityTypeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a custom activity type for a pack.
    User must be a member of the pack.
    """
    # Verify user is a member of the pack
    await verify_pack_member(pack_id, current_user, db)

    # Create the custom activity type
    new_activity_type = ActivityTypeModel(
        name=activity_type_data.name,
        icon=activity_type_data.icon,
        color=activity_type_data.color,
        pack_id=pack_id,
        is_default=False,
    )

    try:
        db.add(new_activity_type)
        db.commit()
        db.refresh(new_activity_type)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Activity type '{activity_type_data.name}' already exists for this pack",
        )

    return new_activity_type
