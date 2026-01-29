from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType

DEFAULT_ACTIVITY_TYPES = [
    {"name": "Walk", "icon": "figure.walk", "color": "#4CAF50"},
    {"name": "Feed", "icon": "fork.knife", "color": "#FF9800"},
    {"name": "Brush teeth", "icon": "mouth", "color": "#2196F3"},
    {"name": "Bath", "icon": "drop.fill", "color": "#00BCD4"},
    {"name": "Medication", "icon": "pills.fill", "color": "#F44336"},
    {"name": "Play", "icon": "gamecontroller.fill", "color": "#E91E63"},
    {"name": "Grooming", "icon": "scissors", "color": "#795548"},
]


def seed_activity_types(db: Session):
    """
    Seed the database with default activity types if they don't exist.

    Default activity types have:
    - pack_id = None (available to all packs)
    - is_default = True
    """
    # Check if default types already exist
    existing_defaults = (
        db.query(ActivityType).filter(ActivityType.is_default.is_(True)).count()
    )

    if existing_defaults == 0:
        default_types = [
            ActivityType(
                name=activity["name"],
                icon=activity["icon"],
                color=activity["color"],
                pack_id=None,
                is_default=True,
            )
            for activity in DEFAULT_ACTIVITY_TYPES
        ]
        db.add_all(default_types)
        db.commit()
        print(f"Seeded {len(default_types)} default activity types")
    else:
        print(f"Default activity types already exist ({existing_defaults} found)")
