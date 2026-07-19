from pydantic import BaseModel, model_validator


class ProfileFilters(BaseModel):
    gender: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    distance: int | None = None
    verified_only: bool = False
    profile_complete_only: bool = False

    @model_validator(mode="after")
    def valid(self):
        if self.age_min is not None and self.age_max is not None and self.age_min > self.age_max:
            raise ValueError("Invalid age range")
        if self.age_min is not None and self.age_min < 18:
            raise ValueError("Minimum age is 18")
        if self.distance is not None and self.distance < 0:
            raise ValueError("Distance must be non-negative")
        return self
