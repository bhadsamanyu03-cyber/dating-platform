from uuid import uuid4
import pytest
from app.domain.discovery.repository import decode_cursor, encode_cursor
from app.domain.discovery.service import DiscoveryError, DiscoveryService
from app.domain.identity.models import User


def test_cursor_round_trip_and_invalid_value() -> None:
    assert decode_cursor(encode_cursor(42)) == 42
    with pytest.raises(ValueError):
        decode_cursor("invalid")


@pytest.mark.asyncio
async def test_cannot_act_on_own_profile() -> None:
    user = User(id=uuid4(), email="discovery@example.com", password_hash="hash")
    with pytest.raises(DiscoveryError, match="own profile"):
        await DiscoveryService(None).like(user, user.id)
