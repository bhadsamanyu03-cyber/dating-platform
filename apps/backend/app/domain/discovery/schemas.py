from datetime import date
from uuid import UUID
from pydantic import BaseModel
from app.domain.profile.schemas import InterestResponse


class DiscoveryAction(BaseModel):
    target_user_id: UUID


class DiscoveryProfile(BaseModel):
    user_id: UUID
    username: str
    display_name: str
    bio: str
    gender: str
    pronouns: str | None
    date_of_birth: date
    height_cm: int | None
    interests: list[InterestResponse]
    profile_completion_percentage: int


class DiscoveryPage(BaseModel):
    candidates: list[DiscoveryProfile]
    next_cursor: str | None
