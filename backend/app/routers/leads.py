from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Lead, User

router = APIRouter(prefix="/api/leads", tags=["leads"])


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    company: str
    website: str | None = None
    status: Literal["new", "contacted", "qualified", "lost"] = "new"

    @field_validator("name", "company")
    @classmethod
    def strip_and_check_length(cls, v: str, info) -> str:
        v = v.strip()
        if not v:
            raise ValueError(f"{info.field_name} must not be blank")
        if len(v) > 100:
            raise ValueError(f"{info.field_name} must be at most 100 characters")
        return v

    @field_validator("email")
    @classmethod
    def email_max_length(cls, v: str) -> str:
        if len(v) > 254:
            raise ValueError("email must be at most 254 characters")
        return v

    @field_validator("website", mode="before")
    @classmethod
    def parse_website(cls, v) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("website must be a string")
        v = v.strip()
        if not v:
            return None
        if len(v) > 255:
            raise ValueError("website must be at most 255 characters")
        if not v.startswith(("http://", "https://")):
            raise ValueError("website must be a valid http or https URL")
        return v


def _lead_dict(lead: Lead, owner_name: str | None = None) -> dict:
    d = {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "company": lead.company,
        "website": lead.website,
        "status": lead.status,
        "owner_id": lead.owner_id,
        "created_at": lead.created_at.isoformat(),
    }
    if owner_name is not None:
        d["owner_name"] = owner_name
    return d


@router.get("")
def list_leads(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role == "admin":
        rows = (
            db.query(Lead, User.name.label("owner_name"))
            .join(User, Lead.owner_id == User.id)
            .order_by(Lead.created_at.desc())
            .all()
        )
        return [_lead_dict(lead, owner_name) for lead, owner_name in rows]

    rows = (
        db.query(Lead)
        .filter(Lead.owner_id == user.id)
        .order_by(Lead.created_at.desc())
        .all()
    )
    return [_lead_dict(lead) for lead in rows]


@router.post("", status_code=201)
def create_lead(
    body: LeadCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = Lead(
        name=body.name,
        email=body.email,
        company=body.company,
        website=body.website,
        status=body.status,
        owner_id=user.id,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return _lead_dict(lead)
