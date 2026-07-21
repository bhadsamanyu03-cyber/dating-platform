from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domain.profile.schemas import ProfilePhotoCreate


def test_profile_photo_accepts_valid_asset_reference() -> None:
    payload = ProfilePhotoCreate(media_asset_id=uuid4(), ordering=11)
    assert payload.ordering == 11


@pytest.mark.parametrize("ordering", [-1, 12])
def test_profile_photo_rejects_invalid_ordering(ordering: int) -> None:
    with pytest.raises(ValidationError):
        ProfilePhotoCreate(media_asset_id=uuid4(), ordering=ordering)
