from datetime import date
import pytest
from pydantic import ValidationError
from app.domain.profile.schemas import ProfileUpdate
from app.domain.profile.service import completeness, is_adult


def payload(**overrides) -> ProfileUpdate:
    values = {
        "username": "valid_user",
        "display_name": "Valid",
        "bio": "About me",
        "gender": "Woman",
        "date_of_birth": "2000-01-01",
        "interest_ids": [],
    }
    values.update(overrides)
    return ProfileUpdate(**values)


def test_username_and_bio_validation() -> None:
    with pytest.raises(ValidationError):
        payload(username="not valid")
    with pytest.raises(ValidationError):
        payload(bio="x" * 151)


def test_adult_age_boundary_and_completion() -> None:
    assert is_adult(date(2000, 1, 1), date(2026, 7, 18))
    assert not is_adult(date(2008, 7, 19), date(2026, 7, 18))
    assert completeness(payload()) == 83
