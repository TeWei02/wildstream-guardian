"""用戶反饋 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.models import Feedback
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.get("")
def list_feedback(
    category: str = Query(None),
    is_resolved: bool = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Feedback)
    if category:
        q = q.filter(Feedback.category == category)
    if is_resolved is not None:
        q = q.filter(Feedback.is_resolved == is_resolved)
    q = q.order_by(Feedback.created_at.desc()).limit(50)
    items = q.all()
    return {"feedback": [f_to_dict(f) for f in items]}


@router.post("")
def submit_feedback(data: dict, db: Session = Depends(get_db)):
    f = Feedback(
        user_name=data.get("user_name", "匿名"),
        email=data.get("email", ""),
        category=data.get("category", "general"),
        subject=data.get("subject", ""),
        message=data.get("message", ""),
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f_to_dict(f)


@router.put("/{feedback_id}/resolve")
def resolve_feedback(feedback_id: int, db: Session = Depends(get_db)):
    f = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not f:
        raise HTTPException(404, "反饋不存在")
    f.is_resolved = True
    db.commit()
    return {"ok": True}


def f_to_dict(f: Feedback):
    return {
        "id": f.id, "user_name": f.user_name, "email": f.email,
        "category": f.category, "subject": f.subject, "message": f.message,
        "is_resolved": f.is_resolved,
        "created_at": f.created_at.isoformat(),
    }
