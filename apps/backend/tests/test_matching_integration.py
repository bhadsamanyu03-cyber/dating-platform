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


def token(user_id: UUID) -> dict[str, str]:
    return {
        "Authorization": "Bearer "
        + create_jwt(
            get_settings().jwt_secret_key.get_secret_value(),
            user_id,
            "access",
            timedelta(minutes=15),
            1,
        )
    }


def user(connection, label: str) -> UUID:
    user_id, profile_id = uuid4(), uuid4()
    connection.execute(
        "INSERT INTO users (id, email, password_hash, is_email_verified, is_active, credential_version) VALUES (%s, %s, 'test', TRUE, TRUE, 1)",
        (user_id, f"match-{label}-{user_id}@example.com"),
    )
    connection.execute(
        "INSERT INTO user_profiles (id, user_id, username, display_name, bio, gender, date_of_birth, profile_completion_percentage) VALUES (%s, %s, %s, %s, '', 'Unspecified', '2000-01-01', 100)",
        (profile_id, user_id, f"match_{label}_{str(user_id)[:8]}", label),
    )
    return user_id


def test_mutual_like_match_lifecycle_authorization_and_empty_list():
    database_url = os.environ["DATABASE_URL"].replace("+asyncpg", "")
    with psycopg.connect(database_url) as connection:
        first, second, outsider = (
            user(connection, "first"),
            user(connection, "second"),
            user(connection, "outsider"),
        )
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/matches", headers=token(first)).json() == {
            "matches": [],
            "next_cursor": None,
        }
        assert (
            client.post(
                "/api/v1/discovery/like", headers=token(first), json={"target_user_id": str(second)}
            ).status_code
            == 204
        )
        assert client.get("/api/v1/matches", headers=token(first)).json()["matches"] == []
        assert (
            client.post(
                "/api/v1/discovery/like", headers=token(second), json={"target_user_id": str(first)}
            ).status_code
            == 204
        )
        assert (
            client.post(
                "/api/v1/discovery/like", headers=token(second), json={"target_user_id": str(first)}
            ).status_code
            == 204
        )
        listing = client.get("/api/v1/matches?limit=1", headers=token(first))
        assert listing.status_code == 200 and len(listing.json()["matches"]) == 1
        match_id = listing.json()["matches"][0]["id"]
        assert client.get(f"/api/v1/matches/{match_id}", headers=token(outsider)).status_code == 404
        assert (
            client.delete(f"/api/v1/matches/{match_id}", headers=token(outsider)).status_code == 404
        )
        assert client.delete(f"/api/v1/matches/{match_id}", headers=token(first)).status_code == 204
        assert client.get("/api/v1/matches", headers=token(first)).json() == {
            "matches": [],
            "next_cursor": None,
        }
    with psycopg.connect(database_url) as connection:
        assert (
            connection.execute(
                "SELECT count(*) FROM matches WHERE (user_one_id = %s AND user_two_id = %s) OR (user_one_id = %s AND user_two_id = %s)",
                (first, second, second, first),
            ).fetchone()[0]
            == 0
        )
        assert (
            connection.execute(
                "SELECT count(*) FROM profile_likes WHERE liker_user_id IN (%s, %s)",
                (first, second),
            ).fetchone()[0]
            == 2
        )
