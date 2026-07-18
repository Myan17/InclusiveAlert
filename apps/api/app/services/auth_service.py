# apps/api/app/services/auth_service.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.user_profile import UserProfile

# bcrypt only inspects the first 72 bytes of a password. Newer bcrypt releases
# raise instead of silently truncating, so we truncate explicitly to keep
# arbitrary-length passwords working consistently.
_BCRYPT_MAX_BYTES = 72

# A throwaway hash used for constant-time verification when no user exists,
# so authentication timing does not leak whether an email is registered.
_DUMMY_HASH = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt())


def _truncate(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_truncate(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("utf-8"))
    except ValueError:
        return False

def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        return None

async def register_user(db: AsyncSession, email: str, password: str, role: str) -> UserProfile:
    existing = await db.execute(select(UserProfile).where(UserProfile.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")
    user = UserProfile(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[UserProfile]:
    result = await db.execute(select(UserProfile).where(UserProfile.email == email))
    user = result.scalar_one_or_none()
    if not user:
        # Constant-time dummy check: prevent email enumeration via timing.
        bcrypt.checkpw(_truncate(password), _DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
