from app.api.router import liveness


async def test_liveness() -> None:
    assert await liveness() == {"status": "ok"}
