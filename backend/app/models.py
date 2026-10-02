from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, func

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'member')", name="ck_users_role"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        CheckConstraint("status IN ('new', 'contacted', 'qualified', 'lost')", name="ck_leads_status"),
        Index("ix_leads_owner_id", "owner_id"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=False)
    website = Column(String, nullable=True)
    status = Column(String, nullable=False, server_default="new")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
