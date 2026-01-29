from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.config import settings
from app.schemas.user import TokenPayload


def create_access_token(user_id: int) -> str:
    """Create a JWT access token for the given user ID."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": user_id,
        "exp": int(expire.timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token for the given user ID."""
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        return TokenPayload(**payload)
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
