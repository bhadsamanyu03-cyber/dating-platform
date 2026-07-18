from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.identity.models import User
from app.domain.profile.models import UserProfile
from app.domain.profile.repository import ProfileRepository
from app.domain.profile.schemas import ProfileUpdate


class ProfileError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message, self.status_code = message, status_code


def is_adult(dob: date, today: date | None = None) -> bool:
    today = today or date.today()
    return (today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))) >= 18


def completeness(payload: ProfileUpdate) -> int:
    fields = [
        payload.display_name,
        payload.username,
        payload.bio,
        payload.gender,
        payload.date_of_birth,
        bool(payload.interest_ids),
    ]
    return round(sum(bool(value) for value in fields) * 100 / len(fields))


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, ProfileRepository(db)

    async def update(self, user: User, payload: ProfileUpdate) -> UserProfile:
        if not is_adult(payload.date_of_birth):
            raise ProfileError("You must be at least 18 years old", 422)
        occupied = await self.repo.by_username(payload.username)
        if occupied and occupied.user_id != user.id:
            raise ProfileError("Username is unavailable", 409)
        interests = await self.repo.interests(payload.interest_ids)
        if len(interests) != len(set(payload.interest_ids)):
            raise ProfileError("One or more interests are invalid", 422)
        profile = await self.repo.by_user(user.id)
        values = payload.model_dump(exclude={"interest_ids"})
        values["profile_completion_percentage"] = completeness(payload)
        if profile is None:
            profile = UserProfile(user_id=user.id, **values)
            self.db.add(profile)
        else:
            for key, value in values.items():
                setattr(profile, key, value)
        profile.interests = interests
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
