# apps/api/app/schemas/auth.py
import uuid
from typing import Literal
from pydantic import BaseModel, EmailStr, ConfigDict

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: Literal["victim", "respondent", "authority"] = "victim"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
