from datetime import timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    create_refresh_token,
    hash_token,
    utcnow,
    verify_password,
)
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import RefreshToken, User

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


def _set_tokens(response: Response, access: str, refresh: str):
    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        samesite="lax",
        secure=settings.SECURE_COOKIES,
        max_age=settings.ACCESS_TOKEN_TTL_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        samesite="lax",
        secure=settings.SECURE_COOKIES,
        max_age=settings.REFRESH_TOKEN_TTL_DAYS * 86400,
        path="/api/auth",
    )


def _clear_tokens(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/auth")


def _user_dict(user: User) -> dict:
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.post("/login")
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access = create_access_token(user.id, user.role)
    raw_refresh, refresh_hash = create_refresh_token()

    db.add(RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        expires_at=utcnow() + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS),
    ))
    db.commit()

    _set_tokens(response, access, raw_refresh)
    return _user_dict(user)


@router.post("/refresh")
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    token_hash = hash_token(refresh_token)
    stored = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if not stored:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Reuse detection: already-revoked token presented again.
    # Revoke every active token for this user — a leaked token could be in
    # an attacker's hands, so kill the whole family.
    if stored.revoked_at is not None:
        db.query(RefreshToken).filter(
            RefreshToken.user_id == stored.user_id,
            RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": utcnow()})
        db.commit()
        _clear_tokens(response)
        raise HTTPException(status_code=401, detail="Refresh token already used")

    if stored.expires_at < utcnow():
        stored.revoked_at = utcnow()
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Rotate: revoke old, issue new
    stored.revoked_at = utcnow()

    user = db.query(User).filter(User.id == stored.user_id).first()
    if not user:
        db.commit()
        raise HTTPException(status_code=401, detail="User not found")

    access = create_access_token(user.id, user.role)
    raw_refresh, refresh_hash = create_refresh_token()

    db.add(RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        expires_at=utcnow() + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS),
    ))
    db.commit()

    _set_tokens(response, access, raw_refresh)
    return _user_dict(user)


@router.post("/logout")
def logout(
    response: Response,
    user: User = Depends(get_current_user),
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if refresh_token:
        token_hash = hash_token(refresh_token)
        stored = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        ).first()
        if stored:
            stored.revoked_at = utcnow()
            db.commit()

    _clear_tokens(response)
    return {"message": "Logged out"}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return _user_dict(user)
