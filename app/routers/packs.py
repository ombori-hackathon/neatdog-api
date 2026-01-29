import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db import get_db
from app.models.pack import Pack
from app.models.pack_invitation import PackInvitation
from app.models.pack_member import PackMember
from app.models.user import User
from app.schemas.pack import (
    AcceptInvitation,
    PackCreate,
    PackInvitationCreate,
    PackWithMembers,
)
from app.schemas.pack import (
    Pack as PackSchema,
)
from app.schemas.pack import (
    PackInvitation as PackInvitationSchema,
)

router = APIRouter(prefix="/packs", tags=["packs"])


async def verify_pack_member(
    pack_id: int,
    user: User,
    db: Session,
    required_roles: list[str] | None = None,
) -> PackMember:
    """
    Verify that a user is a member of a pack and optionally check their role.

    Args:
        pack_id: The pack ID to check
        user: The current user
        db: Database session
        required_roles: Optional list of roles that are allowed (e.g., ['owner', 'admin'])

    Returns:
        The PackMember record

    Raises:
        HTTPException: If user is not a member or doesn't have the required role
    """
    # Check if pack exists
    pack = db.query(Pack).filter(Pack.id == pack_id).first()
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pack not found"
        )

    # Check membership
    member = (
        db.query(PackMember)
        .filter(PackMember.pack_id == pack_id, PackMember.user_id == user.id)
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this pack",
        )

    # Check role if required
    if required_roles and member.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}",
        )

    return member


@router.post("", response_model=PackSchema, status_code=status.HTTP_201_CREATED)
async def create_pack(
    pack_data: PackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new pack. The creator automatically becomes the owner.
    """
    # Create the pack
    new_pack = Pack(
        name=pack_data.name,
        created_by=current_user.id,
    )
    db.add(new_pack)
    db.flush()  # Get the pack ID

    # Create the owner membership
    owner_member = PackMember(
        pack_id=new_pack.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(owner_member)
    db.commit()
    db.refresh(new_pack)

    return new_pack


@router.get("", response_model=list[PackSchema])
async def list_packs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all packs that the current user is a member of.
    """
    # Get all pack memberships for the user
    memberships = (
        db.query(PackMember).filter(PackMember.user_id == current_user.id).all()
    )

    # Get the packs
    pack_ids = [m.pack_id for m in memberships]
    packs = db.query(Pack).filter(Pack.id.in_(pack_ids)).all()

    return packs


@router.get("/{pack_id}", response_model=PackWithMembers)
async def get_pack(
    pack_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get pack details with members. User must be a member of the pack.
    """
    # Verify membership
    await verify_pack_member(pack_id, current_user, db)

    # Get the pack with members
    pack = db.query(Pack).filter(Pack.id == pack_id).first()

    return pack


@router.post(
    "/{pack_id}/invitations",
    response_model=PackInvitationSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_invitation(
    pack_id: int,
    invitation_data: PackInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Invite a user to a pack by email. Only owners and admins can invite.
    """
    # Verify user is owner or admin
    await verify_pack_member(
        pack_id, current_user, db, required_roles=["owner", "admin"]
    )

    # Check if user is already a member
    existing_user = db.query(User).filter(User.email == invitation_data.email).first()
    if existing_user:
        existing_member = (
            db.query(PackMember)
            .filter(
                PackMember.pack_id == pack_id, PackMember.user_id == existing_user.id
            )
            .first()
        )
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this pack",
            )

    # Check if there's already a pending invitation
    existing_invitation = (
        db.query(PackInvitation)
        .filter(
            PackInvitation.pack_id == pack_id,
            PackInvitation.email == invitation_data.email,
            PackInvitation.accepted_at.is_(None),
            PackInvitation.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An invitation for this email already exists",
        )

    # Create the invitation
    invitation = PackInvitation(
        pack_id=pack_id,
        email=invitation_data.email,
        token=secrets.token_urlsafe(32),
        invited_by=current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation


@router.post("/invitations/accept", response_model=PackSchema)
async def accept_invitation(
    accept_data: AcceptInvitation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accept a pack invitation using the invitation token.
    """
    # Find the invitation
    invitation = (
        db.query(PackInvitation)
        .filter(PackInvitation.token == accept_data.token)
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    # Check if invitation has expired
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    # Check if invitation has already been accepted
    if invitation.accepted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has already been accepted",
        )

    # Check if the current user's email matches the invitation email
    if current_user.email != invitation.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is for a different email address",
        )

    # Check if user is already a member
    existing_member = (
        db.query(PackMember)
        .filter(
            PackMember.pack_id == invitation.pack_id,
            PackMember.user_id == current_user.id,
        )
        .first()
    )

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this pack",
        )

    # Create the membership
    new_member = PackMember(
        pack_id=invitation.pack_id,
        user_id=current_user.id,
        role="member",
    )
    db.add(new_member)

    # Mark invitation as accepted
    invitation.accepted_at = datetime.utcnow()

    db.commit()

    # Return the pack
    pack = db.query(Pack).filter(Pack.id == invitation.pack_id).first()
    return pack
