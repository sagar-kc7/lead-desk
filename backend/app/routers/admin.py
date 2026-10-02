from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    rows = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at.isoformat(),
        }
        for u in rows
    ]
