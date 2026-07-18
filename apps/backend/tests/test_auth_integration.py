import os
import pytest

if not os.getenv("RUN_INTEGRATION_TESTS"):
    pytest.skip("requires PostgreSQL and Redis services", allow_module_level=True)

from fastapi.testclient import TestClient
from app.main import create_app


def test_register_login_refresh_replay_and_logout() -> None:
    with TestClient(create_app()) as client:
        registration = client.post(
            "/api/v1/auth/register",
            json={"email": "identity-test@example.com", "password": "SecurePassword123"},
        )
        assert registration.status_code == 201

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "identity-test@example.com", "password": "SecurePassword123"},
        )
        assert login.status_code == 200
        tokens = login.json()

        me = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        assert me.status_code == 200
        assert me.json()["email"] == "identity-test@example.com"

        rotation = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert rotation.status_code == 200
        replay = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert replay.status_code == 401
        logout = client.post(
            "/api/v1/auth/logout", json={"refresh_token": rotation.json()["refresh_token"]}
        )
        assert logout.status_code == 204

        profile = client.put(
            "/api/v1/profile/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"username": "identity_test", "display_name": "Identity Test", "bio": "", "gender": "Unspecified", "date_of_birth": "2000-01-01", "interest_ids": []},
        )
        assert profile.status_code == 200
        assert profile.json()["profile_completion_percentage"] == 67
        public = client.get("/api/v1/profile/identity_test")
        assert public.status_code == 200
