from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db import get_db
from app.models.dog import Dog as DogModel
from app.models.user import User
from app.routers.packs import verify_pack_member
from app.schemas.dog import Dog, DogCreate, DogUpdate

router = APIRouter()


@router.post(
    "/packs/{pack_id}/dog",
    response_model=Dog,
    status_code=status.HTTP_201_CREATED,
    tags=["dogs"],
)
async def add_dog(
    pack_id: int,
    dog_data: DogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a dog to a pack. User must be a member of the pack.
    Each pack can only have one dog.
    """
    # Verify user is a member of the pack
    await verify_pack_member(pack_id, current_user, db)

    # Check if pack already has a dog
    existing_dog = db.query(DogModel).filter(DogModel.pack_id == pack_id).first()
    if existing_dog:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This pack already has a dog",
        )

    # Create the dog
    new_dog = DogModel(
        pack_id=pack_id,
        name=dog_data.name,
        breed=dog_data.breed,
        birth_date=dog_data.birth_date,
        photo_url=dog_data.photo_url,
    )
    db.add(new_dog)
    db.commit()
    db.refresh(new_dog)

    return new_dog


@router.get("/packs/{pack_id}/dog", response_model=Dog, tags=["dogs"])
async def get_dog(
    pack_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the dog profile for a pack. User must be a member of the pack.
    """
    # Verify user is a member of the pack
    await verify_pack_member(pack_id, current_user, db)

    # Get the dog
    dog = db.query(DogModel).filter(DogModel.pack_id == pack_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dog found for this pack",
        )

    return dog


@router.patch("/packs/{pack_id}/dog", response_model=Dog, tags=["dogs"])
async def update_dog(
    pack_id: int,
    dog_data: DogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a dog's information. User must be a member of the pack.
    """
    # Verify user is a member of the pack
    await verify_pack_member(pack_id, current_user, db)

    # Get the dog
    dog = db.query(DogModel).filter(DogModel.pack_id == pack_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dog found for this pack",
        )

    # Update only provided fields
    if dog_data.name is not None:
        dog.name = dog_data.name
    if dog_data.breed is not None:
        dog.breed = dog_data.breed
    if dog_data.birth_date is not None:
        dog.birth_date = dog_data.birth_date
    if dog_data.photo_url is not None:
        dog.photo_url = dog_data.photo_url

    db.commit()
    db.refresh(dog)

    return dog
