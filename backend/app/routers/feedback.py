from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.collection_request import CollectionRequest
from backend.app.models.feedback import Feedback
from backend.app.models.user import User
from backend.app.schemas.waste_management import FeedbackCreate, FeedbackResponse

router = APIRouter()


@router.get("/", response_model=list[FeedbackResponse])
def list_feedback(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    query = db.query(Feedback)
    if current_user.role != "admin":
        query = query.filter(Feedback.user_id == current_user.id)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    collection = db.query(CollectionRequest).filter(CollectionRequest.id == payload.collection_request_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection request not found")
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only provide feedback for your own collection")
    if collection.status != "completed":
        raise HTTPException(status_code=400, detail="Feedback is only allowed after the collection is completed")
    if db.query(Feedback).filter(Feedback.collection_request_id == payload.collection_request_id).first():
        raise HTTPException(status_code=400, detail="Feedback already exists for this collection request")

    feedback = Feedback(
        user_id=current_user.id,
        collection_request_id=payload.collection_request_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
