from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.auth.deps import get_current_user
from app.db import get_db
from app.models.activity_log import ActivityLog
from app.models.activity_type import ActivityType
from app.models.dog import Dog
from app.models.user import User
from app.routers.packs import verify_pack_member
from app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogWithDetails,
)

router = APIRouter()


@router.post(
    "/packs/{pack_id}/activities",
    response_model=ActivityLogWithDetails,
    status_code=status.HTTP_201_CREATED,
    tags=["activities"],
)
async def log_activity(
    pack_id: int,
    activity_data: ActivityLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Log an activity for the pack's dog. User must be a pack member.
    """
    # Verify user is a member of the pack
    await verify_pack_member(pack_id, current_user, db)

    # Check if pack has a dog
    dog = db.query(Dog).filter(Dog.pack_id == pack_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pack does not have a dog",
        )

    # Verify activity type exists
    activity_type = (
        db.query(ActivityType)
        .filter(ActivityType.id == activity_data.activity_type_id)
        .first()
    )
    if not activity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity type not found",
        )

    # If it's a custom activity type, verify it belongs to this pack
    if activity_type.pack_id is not None and activity_type.pack_id != pack_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity type belongs to a different pack",
        )

    # Create the activity log
    activity_log = ActivityLog(
        pack_id=pack_id,
        dog_id=dog.id,
        activity_type_id=activity_data.activity_type_id,
        user_id=current_user.id,
        notes=activity_data.notes,
        logged_at=activity_data.logged_at or datetime.utcnow(),
    )
    db.add(activity_log)
    db.commit()
    db.refresh(activity_log)

    # Fetch with relationships for response
    activity_log_with_details = (
        db.query(ActivityLog)
        .options(
            joinedload(ActivityLog.activity_type),
            joinedload(ActivityLog.user),
        )
        .filter(ActivityLog.id == activity_log.id)
        .first()
    )

    return activity_log_with_details


@router.get(
    "/packs/{pack_id}/activities",
    response_model=list[ActivityLogWithDetails],
    tags=["activities"],
)
async def get_activity_history(
    pack_id: int,
    activity_type_id: int | None = Query(None, description="Filter by activity type"),
    start_date: datetime | None = Query(None, description="Filter from this date"),
    end_date: datetime | None = Query(None, description="Filter to this date"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get activity history for a pack. User must be a pack member.
    Results are sorted by logged_at descending (newest first).
    """
    # Verify user is a member of the pack
    await verify_pack_member(pack_id, current_user, db)

    # Build query
    query = (
        db.query(ActivityLog)
        .options(
            joinedload(ActivityLog.activity_type),
            joinedload(ActivityLog.user),
        )
        .filter(ActivityLog.pack_id == pack_id)
    )

    # Apply filters
    if activity_type_id is not None:
        query = query.filter(ActivityLog.activity_type_id == activity_type_id)
    if start_date is not None:
        query = query.filter(ActivityLog.logged_at >= start_date)
    if end_date is not None:
        query = query.filter(ActivityLog.logged_at <= end_date)

    # Sort by logged_at descending (newest first)
    query = query.order_by(ActivityLog.logged_at.desc())

    # Apply pagination
    activities = query.offset(offset).limit(limit).all()

    return activities
