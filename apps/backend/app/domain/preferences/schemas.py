from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.domain.preferences.models import PreferredGender


class DiscoveryPreferenceUpdate(BaseModel):
    preferred_gender: PreferredGender = PreferredGender.ALL
    minimum_age: int = Field(default=18, ge=18, le=120)
    maximum_age: int = Field(default=120, ge=18, le=120)
    maximum_distance_km: int = Field(default=100, ge=1, le=10000)
    show_verified_only: bool = False
    show_only_with_photos: bool = False

    @model_validator(mode="after")
    def valid_age_range(self):
        if self.minimum_age > self.maximum_age:
            raise ValueError("Minimum age cannot exceed maximum age")
        return self


class DiscoveryPreferenceResponse(DiscoveryPreferenceUpdate):
    created_at: datetime
    updated_at: datetime
