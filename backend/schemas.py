from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)
    nickname: str = Field(min_length=2, max_length=32, pattern=r"^[A-Za-z0-9_\-]+$")


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nickname: str


class ScoreIn(BaseModel):
    score: int = Field(ge=0, le=10_000_000)
    lines: int = Field(ge=0, le=1_000_000)
    level: int = Field(ge=1, le=99)


class ScoreOut(BaseModel):
    id: int
    score: int
    lines: int
    level: int
    played_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    nickname: str
    score: int
    lines: int
    level: int
    played_at: datetime
