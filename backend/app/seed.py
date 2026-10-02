from app.auth import pwd_context
from app.database import SessionLocal
from app.models import Lead, User

USERS = [
    {"name": "Admin", "email": "admin@leaddesk.test", "password": "Admin@123", "role": "admin"},
    {"name": "Member", "email": "member@leaddesk.test", "password": "Member@123", "role": "member"},
]

LEADS = {
    "admin@leaddesk.test": [
        {"name": "Alice Johnson", "email": "alice@techcorp.com", "company": "TechCorp", "status": "new"},
        {"name": "Bob Williams", "email": "bob@globalinc.com", "company": "Global Inc", "website": "https://globalinc.example.com", "status": "contacted"},
        {"name": "Carol Davis", "email": "carol@startupx.com", "company": "StartupX", "status": "qualified"},
    ],
    "member@leaddesk.test": [
        {"name": "Dave Brown", "email": "dave@acmellc.com", "company": "Acme LLC", "status": "new"},
        {"name": "Eve Martinez", "email": "eve@netserv.com", "company": "NetServ", "website": "https://netserv.example.com", "status": "contacted"},
        {"name": "Frank Lee", "email": "frank@dataflow.com", "company": "DataFlow", "status": "qualified"},
        {"name": "Grace Kim", "email": "grace@cloudco.com", "company": "CloudCo", "status": "lost"},
    ],
}


def seed():
    db = SessionLocal()
    try:
        if db.query(User).first():
            return

        users = {}
        for u in USERS:
            user = User(
                name=u["name"],
                email=u["email"],
                password_hash=pwd_context.hash(u["password"]),
                role=u["role"],
            )
            db.add(user)
            db.flush()
            users[u["email"]] = user

        for email, leads in LEADS.items():
            for lead_data in leads:
                db.add(Lead(owner_id=users[email].id, **lead_data))

        db.commit()
        print("Seed data inserted.")
    finally:
        db.close()
