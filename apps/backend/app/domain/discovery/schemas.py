from uuid import UUID
from pydantic import BaseModel, Field, model_validator
from app.domain.profile.schemas import InterestResponse


class DiscoveryAction(BaseModel):
    target_user_id: UUID


class DiscoveryFilters(BaseModel):
    min_age: int | None = Field(default=None, ge=18, le=120)
    max_age: int | None = Field(default=None, ge=18, le=120)
    gender: str | None = Field(default=None, min_length=1, max_length=100)
    minimum_profile_completion: int = Field(default=100, ge=0, le=100)
    verified_only: bool = False
    active_recently: bool = False
    show_only_with_photos: bool = False

    @model_validator(mode="after")
    def valid_age_range(self):
        if self.min_age and self.max_age and self.min_age > self.max_age:
            raise ValueError("Minimum age cannot exceed maximum age")
        return self


class DiscoveryProfile(BaseModel):
    user_id: UUID
    username: str
    display_name: str
    bio: str
    gender: str
    pronouns: str | None
    age: int
    height_cm: int | None
    interests: list[InterestResponse]
    profile_completion_percentage: int


class DiscoveryPage(BaseModel):
    candidates: list[DiscoveryProfile]
    next_cursor: str | None
