from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import re

USERNAME = re.compile(r"^[A-Za-z0-9_]{3,30}$")


class ProfileUpdate(BaseModel):
    username: str
    display_name: str = Field(min_length=1, max_length=100)
    bio: str = Field(max_length=150)
    gender: str = Field(min_length=1, max_length=100)
    pronouns: str | None = Field(default=None, max_length=100)
    date_of_birth: date
    height_cm: int | None = Field(default=None, ge=1, le=300)
    interest_ids: list[UUID] = Field(default_factory=list)

    @field_validator("username")
    @classmethod
    def username_format(cls, value: str) -> str:
        if not USERNAME.fullmatch(value):
            raise ValueError("Username must be 3-30 letters, numbers, or underscores")
        return value


class InterestResponse(BaseModel):
    id: UUID
    name: str


class ProfileResponse(BaseModel):
    username: str
    display_name: str
    bio: str
    gender: str
    pronouns: str | None
    date_of_birth: date
    height_cm: int | None
    interests: list[InterestResponse]
    profile_photo_count: int
    profile_video_count: int
    profile_completion_percentage: int
    created_at: datetime
    updated_at: datetime


class UsernameAvailability(BaseModel):
    username: str
    available: bool
