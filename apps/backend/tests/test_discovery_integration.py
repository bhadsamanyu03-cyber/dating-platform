"""PostgreSQL-backed discovery repository and API coverage."""

import os
from datetime import timedelta
from uuid import UUID, uuid4

import psycopg
import pytest

if not os.getenv("RUN_INTEGRATION_TESTS"):
    pytest.skip("requires PostgreSQL and Redis services", allow_module_level=True)

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.domain.identity.security import create_jwt
from app.main import create_app


def database():
    return psycopg.connect(os.environ["DATABASE_URL"].replace("+asyncpg", ""))


def authorization(user_id: UUID) -> dict[str, str]:
    token = create_jwt(
        get_settings().jwt_secret_key.get_secret_value(),
        user_id,
        "access",
        timedelta(minutes=15),
        1,
    )
    return {"Authorization": f"Bearer {token}"}


def seed_profile(
    connection, label: str, *, completion: int = 100, active: bool = True, deleted: bool = False
) -> tuple[UUID, UUID]:
    user_id, profile_id = uuid4(), uuid4()
    connection.execute(
        """
        INSERT INTO users (id, email, password_hash, is_email_verified, is_active, credential_version, deleted_at)
        VALUES (%s, %s, 'test-hash', TRUE, %s, 1, CASE WHEN %s THEN now() ELSE NULL END)
        """,
        (user_id, f"discovery-{label}-{user_id}@example.com", active, deleted),
    )
    connection.execute(
        """
        INSERT INTO user_profiles
            (id, user_id, username, display_name, bio, gender, date_of_birth,
             profile_completion_percentage)
        VALUES (%s, %s, %s, %s, '', 'Unspecified', '2000-01-01', %s)
        """,
        (profile_id, user_id, f"d_{label[:8]}_{str(user_id)[:8]}", label, completion),
    )
    return user_id, profile_id


def add_interest(connection, profile_id: UUID, interest_id: UUID) -> None:
    connection.execute(
        "INSERT INTO profile_interests (profile_id, interest_id) VALUES (%s, %s)",
        (profile_id, interest_id),
    )


def test_repository_api_filtering_ranking_and_keyset_pagination() -> None:
    with database() as connection:
        actor, actor_profile = seed_profile(connection, "actor")
        high, high_profile = seed_profile(connection, "high")
        middle, middle_profile = seed_profile(connection, "middle")
        low, _ = seed_profile(connection, "low")
        liked, _ = seed_profile(connection, "liked")
        passed, _ = seed_profile(connection, "passed")
        _, _ = seed_profile(connection, "inactive", active=False)
        _, _ = seed_profile(connection, "deleted", deleted=True)
        interest_one, interest_two = uuid4(), uuid4()
        connection.execute(
            "INSERT INTO interests (id, name) VALUES (%s, %s), (%s, %s)",
            (interest_one, f"i-{interest_one}", interest_two, f"i-{interest_two}"),
        )
        for profile_id in (actor_profile, high_profile):
            add_interest(connection, profile_id, interest_one)
        for profile_id in (actor_profile, high_profile, middle_profile):
            add_interest(connection, profile_id, interest_two)
        connection.execute(
            "INSERT INTO profile_likes (id, liker_user_id, liked_user_id) VALUES (%s, %s, %s)",
            (uuid4(), actor, liked),
        )
        connection.execute(
            "INSERT INTO profile_passes (id, passer_user_id, passed_user_id) VALUES (%s, %s, %s)",
            (uuid4(), actor, passed),
        )

    with TestClient(create_app()) as client:
        first = client.get("/api/v1/discovery?limit=2", headers=authorization(actor))
        assert first.status_code == 200
        first_page = first.json()
        assert [candidate["user_id"] for candidate in first_page["candidates"]] == [
            str(high),
            str(middle),
        ]
        assert "date_of_birth" not in first_page["candidates"][0]
        assert isinstance(first_page["candidates"][0]["age"], int)
        assert first_page["next_cursor"]

        second = client.get(
            "/api/v1/discovery",
            params={"limit": 2, "cursor": first_page["next_cursor"]},
            headers=authorization(actor),
        )
        assert second.status_code == 200
        second_page_ids = [candidate["user_id"] for candidate in second.json()["candidates"]]
        assert str(low) in second_page_ids
        assert str(high) not in second_page_ids and str(middle) not in second_page_ids
        assert second.json()["next_cursor"] is None


def test_duplicate_actions_are_idempotent_and_empty_stack_is_returned() -> None:
    with database() as connection:
        actor, _ = seed_profile(connection, "action-actor")
        target, _ = seed_profile(connection, "action-target")

    with TestClient(create_app()) as client:
        for _ in range(2):
            response = client.post(
                "/api/v1/discovery/like",
                headers=authorization(actor),
                json={"target_user_id": str(target)},
            )
            assert response.status_code == 204
        assert (
            client.post(
                "/api/v1/discovery/like",
                headers=authorization(actor),
                json={"target_user_id": str(actor)},
            ).status_code
            == 422
        )
        empty = client.get("/api/v1/discovery", headers=authorization(actor))
        assert empty.status_code == 200
        assert empty.json() == {"candidates": [], "next_cursor": None}

    with database() as connection:
        count = connection.execute(
            "SELECT count(*) FROM profile_likes WHERE liker_user_id = %s AND liked_user_id = %s",
            (actor, target),
        ).fetchone()[0]
        assert count == 1


def test_incomplete_profiles_cannot_access_discovery() -> None:
    with database() as connection:
        incomplete, _ = seed_profile(connection, "incomplete", completion=83)
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/discovery", headers=authorization(incomplete))
    assert response.status_code == 403
