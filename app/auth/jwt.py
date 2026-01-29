import time

from jose import JWTError, jwt

from app.config import settings
from app.schemas.user import TokenPayload


def create_access_token(user_id: int) -> str:
    """Create a JWT access token for the given user ID."""
    expire = int(time.time()) + (settings.access_token_expire_minutes * 60)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token for the given user ID."""
    expire = int(time.time()) + (settings.refresh_token_expire_days * 24 * 60 * 60)
    payload = {
        "sub": str(user_id),
        "exp": expire,
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
