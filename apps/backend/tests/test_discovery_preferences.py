from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domain.discovery.schemas import DiscoveryFilters
from app.domain.discovery.service import DiscoveryService
from app.domain.identity.models import User
from app.domain.preferences.models import PreferredGender
from app.domain.preferences.schemas import DiscoveryPreferenceUpdate
from app.domain.preferences.service import DiscoveryPreferenceService


class Database:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1

    async def refresh(self, _):
        pass


class PreferenceRepository:
    def __init__(self):
        self.value = None

    async def by_user(self, _):
        return self.value

    async def create(self, value):
        value.created_at = datetime.now(timezone.utc)
        value.updated_at = value.created_at
        self.value = value
        return value


@pytest.mark.asyncio
async def test_preference_update_persists_for_authenticated_user():
    user_id = uuid4()
    service = DiscoveryPreferenceService(Database())
    service.repo = PreferenceRepository()
    response = await service.update(
        user_id,
        DiscoveryPreferenceUpdate(
            preferred_gender=PreferredGender.WOMAN,
            minimum_age=21,
            maximum_age=40,
            maximum_distance_km=25,
            show_verified_only=True,
            show_only_with_photos=True,
        ),
    )
    assert response.preferred_gender is PreferredGender.WOMAN
    assert service.repo.value.user_id == user_id and response.show_only_with_photos


def test_preference_validation_rejects_invalid_ranges_distance_and_gender():
    with pytest.raises(ValidationError, match="Minimum age"):
        DiscoveryPreferenceUpdate(minimum_age=40, maximum_age=21)
    with pytest.raises(ValidationError):
        DiscoveryPreferenceUpdate(maximum_distance_km=0)
    with pytest.raises(ValidationError):
        DiscoveryPreferenceUpdate(preferred_gender="Invalid")


class DiscoveryRepository:
    def __init__(self, profile):
        self.profile, self.filters = profile, None

    async def profile_for_user(self, _):
        return self.profile

    async def candidates(self, _, __, ___, ____, filters):
        self.filters = filters
        return []


class Preferences:
    async def filters(self, _):
        return DiscoveryFilters(gender="Woman", min_age=21, max_age=40, show_only_with_photos=True)


@pytest.mark.asyncio
async def test_discovery_uses_stored_preferences_only_without_explicit_filters():
    user_id = uuid4()
    profile = SimpleNamespace(profile_completion_percentage=100, interests=[])
    service = DiscoveryService(Database())
    service.repo = DiscoveryRepository(profile)
    service.preferences = Preferences()
    user = User(id=user_id, email="preferences@example.com", password_hash="x")
    await service.discover(user, None, 20, DiscoveryFilters(), has_explicit_filters=False)
    assert service.repo.filters.gender == "Woman" and service.repo.filters.show_only_with_photos
    explicit = DiscoveryFilters(gender="Man")
    await service.discover(user, None, 20, explicit, has_explicit_filters=True)
    assert service.repo.filters.gender == "Man"
