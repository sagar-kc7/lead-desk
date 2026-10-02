"""Group 3: member gets 403 on /api/admin/users, admin gets 200.
   Group 4: member sees only their own leads."""

from conftest import PASSWORD
from app.models import Lead


# -- Group 3 ----------------------------------------------------------------

def test_member_gets_403_on_admin_users(client, member):
    client.post("/api/auth/login", json={
        "email": "member@test.com", "password": PASSWORD,
    })
    resp = client.get("/api/admin/users")
    assert resp.status_code == 403
    assert "error" in resp.json()


def test_admin_gets_200_on_admin_users(client, admin):
    client.post("/api/auth/login", json={
        "email": "admin@test.com", "password": PASSWORD,
    })
    resp = client.get("/api/admin/users")
    assert resp.status_code == 200

    users = resp.json()
    assert len(users) >= 1
    assert all("password_hash" not in u for u in users)


# -- Group 4 ----------------------------------------------------------------

def test_member_only_sees_own_leads(client, member, admin, db):
    # Insert leads owned by each user directly in the test DB
    db.add_all([
        Lead(name="Member Lead", email="m@x.com", company="MCo",
             owner_id=member.id),
        Lead(name="Admin Lead", email="a@x.com", company="ACo",
             owner_id=admin.id),
    ])
    db.commit()

    # Login as member
    client.post("/api/auth/login", json={
        "email": "member@test.com", "password": PASSWORD,
    })
    resp = client.get("/api/leads")
    assert resp.status_code == 200

    leads = resp.json()
    assert len(leads) == 1
    assert leads[0]["name"] == "Member Lead"
    assert leads[0]["owner_id"] == member.id
