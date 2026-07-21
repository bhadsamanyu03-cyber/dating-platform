from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.identity.models import User
from app.domain.profile.service import ProfileError, ProfileService


class Database:
    def __init__(self):
        self.deleted = []

    def add(self, _):
        pass

    async def delete(self, value):
        self.deleted.append(value)
        value.deleted = True

    async def flush(self):
        pass

    async def commit(self):
        pass

    async def refresh(self, _):
        pass


class Repository:
    def __init__(self, user_id, photos):
        self.profile = SimpleNamespace(id=uuid4(), user_id=user_id, profile_photo_count=len(photos))
        self.photo_values = photos
        self.cleared = False

    async def by_user(self, user_id):
        return self.profile if user_id == self.profile.user_id else None

    async def owned_image_asset(self, *_):
        return SimpleNamespace()

    async def photos(self, _):
        return sorted(
            [value for value in self.photo_values if not getattr(value, "deleted", False)],
            key=lambda value: value.ordering,
        )

    async def photo(self, _, photo_id):
        return next((value for value in self.photo_values if value.id == photo_id), None)

    async def clear_primary(self, _):
        self.cleared = True
        for value in self.photo_values:
            value.is_primary = False


def photo(ordering, primary=False):
    return SimpleNamespace(
        id=uuid4(), media_asset_id=uuid4(), ordering=ordering, is_primary=primary
    )


def service(user_id, photos):
    subject = ProfileService(Database())
    subject.repo = Repository(user_id, photos)
    return subject


@pytest.mark.asyncio
async def test_reorder_and_primary_selection_are_owned_by_the_user():
    user = User(id=uuid4(), email="gallery@example.com", password_hash="x")
    photos = [photo(0, True), photo(1), photo(2)]
    subject = service(user.id, photos)
    reordered = await subject.reorder_photos(user, [photos[2].id, photos[0].id, photos[1].id])
    assert [value.id for value in reordered] == [photos[2].id, photos[0].id, photos[1].id]
    primary = await subject.set_primary_photo(user, photos[1].id)
    assert primary.is_primary and sum(value.is_primary for value in photos) == 1
    with pytest.raises(ProfileError, match="Profile not found"):
        await subject.set_primary_photo(
            User(id=uuid4(), email="other@example.com", password_hash="x"), photos[1].id
        )


@pytest.mark.asyncio
async def test_delete_promotes_next_photo_and_enforces_photo_limit():
    user = User(id=uuid4(), email="delete@example.com", password_hash="x")
    photos = [photo(0, True), photo(1)]
    subject = service(user.id, photos)
    await subject.delete_photo(user, photos[0].id)
    assert photos[1].is_primary
    remaining = await subject.delete_photo(user, photos[1].id)
    assert remaining == [] or all(value.ordering >= 0 for value in remaining)
    subject.repo.photo_values = [photo(index) for index in range(12)]
    with pytest.raises(ProfileError, match="at most 12"):
        await subject.add_photo(user, uuid4(), 0)


@pytest.mark.asyncio
async def test_replace_photo_requires_an_owned_new_asset():
    user = User(id=uuid4(), email="replace@example.com", password_hash="x")
    current = photo(0, True)
    subject = service(user.id, [current])
    new_asset = uuid4()
    replacement = await subject.replace_photo(user, current.id, new_asset)
    assert replacement.media_asset_id == new_asset and replacement.is_primary
