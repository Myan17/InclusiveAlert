# apps/api/app/services/auth_service.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.user_profile import UserProfile

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

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
        pwd_context.dummy_verify()  # Constant-time: prevent email enumeration
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
