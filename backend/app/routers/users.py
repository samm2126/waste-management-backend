from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import get_current_user, require_roles
from backend.app.models.user import User
from backend.app.models.collection_request import CollectionRequest
from backend.app.models.waste_report import WasteReport
from backend.app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.phone is not None:
        current_user.phone = payload.phone
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/reports")
def my_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    return db.query(WasteReport).filter(WasteReport.user_id == current_user.id).offset(skip).limit(limit).all()


@router.get("/collections")
def my_collections(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    return (
        db.query(CollectionRequest)
        .filter((CollectionRequest.user_id == current_user.id) | (CollectionRequest.assigned_collector_id == current_user.id))
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/all", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
