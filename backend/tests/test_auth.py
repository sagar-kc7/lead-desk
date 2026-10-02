"""Group 1: login sets cookies / rejects bad password.
   Group 2: refresh rotates tokens / reuse is rejected."""

from conftest import PASSWORD


# -- Group 1 ----------------------------------------------------------------

def test_login_correct_sets_both_cookies(client, member):
    resp = client.post("/api/auth/login", json={
        "email": "member@test.com", "password": PASSWORD,
    })
    assert resp.status_code == 200
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies

    body = resp.json()
    assert body["id"] == member.id
    assert body["role"] == "member"
    assert "password_hash" not in body


def test_login_wrong_password_returns_401(client, member):
    resp = client.post("/api/auth/login", json={
        "email": "member@test.com", "password": "wrong",
    })
    assert resp.status_code == 401
    assert "error" in resp.json()


# -- Group 2 ----------------------------------------------------------------

def test_refresh_returns_new_tokens(client, member):
    login = client.post("/api/auth/login", json={
        "email": "member@test.com", "password": PASSWORD,
    })
    old_refresh = login.cookies["refresh_token"]

    refresh = client.post("/api/auth/refresh")
    assert refresh.status_code == 200
    assert "access_token" in refresh.cookies
    assert refresh.cookies["refresh_token"] != old_refresh

    # New access token works
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "member@test.com"


def test_reuse_old_refresh_token_fails(client, member):
    login = client.post("/api/auth/login", json={
        "email": "member@test.com", "password": PASSWORD,
    })
    old_refresh = login.cookies["refresh_token"]

    # First refresh succeeds and rotates the token
    resp = client.post("/api/auth/refresh")
    assert resp.status_code == 200

    # Replay the old token on a fresh client (no valid cookies)
    replay = TestClient(app)
    replay.cookies.set("refresh_token", old_refresh)
    resp = replay.post("/api/auth/refresh")
    assert resp.status_code == 401
    assert "already used" in resp.json()["error"].lower()


# Re-export for the replay test above
from fastapi.testclient import TestClient
from app.main import app
