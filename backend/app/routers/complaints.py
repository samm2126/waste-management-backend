from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import get_current_user, require_roles
from backend.app.models.complaint import Complaint
from backend.app.models.user import User
from backend.app.schemas.waste_management import ComplaintCreate, ComplaintResponse, ComplaintUpdate

router = APIRouter()


@router.get("/", response_model=list[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), status_filter: str | None = Query(None, alias="status")):
    query = db.query(Complaint)
    if current_user.role != "admin":
        query = query.filter(Complaint.user_id == current_user.id)
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=ComplaintResponse)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    complaint = Complaint(
        complaint_id=f"CMP-{uuid4().hex[:8].upper()}",
        user_id=current_user.id,
        complaint_type=payload.complaint_type,
        description=payload.description,
        location=payload.location,
        status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(complaint_id: int, payload: ComplaintUpdate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if payload.complaint_type is not None:
        complaint.complaint_type = payload.complaint_type
    if payload.description is not None:
        complaint.description = payload.description
    if payload.location is not None:
        complaint.location = payload.location
    if payload.status is not None:
        complaint.status = payload.status
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint
