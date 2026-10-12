from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.collector_profile import CollectorProfile
from backend.app.models.user import User
from backend.app.schemas.waste_management import CollectorProfileCreate, CollectorProfileResponse

router = APIRouter()


@router.get("/", response_model=list[CollectorProfileResponse])
def list_collectors(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    if current_user.role not in {"admin", "collector"}:
        raise HTTPException(status_code=403, detail="Only collectors and admins can view collector profiles")
    return db.query(CollectorProfile).offset(skip).limit(limit).all()


@router.get("/{collector_id}", response_model=CollectorProfileResponse)
def get_collector_profile(collector_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(CollectorProfile).filter(CollectorProfile.user_id == collector_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Collector profile not found")
    if current_user.role not in {"admin", "collector"} and current_user.id != collector_id:
        raise HTTPException(status_code=403, detail="You do not have access to this profile")
    return profile


@router.post("/profile", response_model=CollectorProfileResponse)
def create_or_update_collector_profile(payload: CollectorProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(CollectorProfile).filter(CollectorProfile.user_id == current_user.id).first()
    if existing is not None:
        existing.specialization = payload.specialization
        existing.vehicle_type = payload.vehicle_type
        if payload.rating is not None:
            existing.rating = payload.rating
        if payload.total_collections is not None:
            existing.total_collections = payload.total_collections
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    current_user.role = "collector"
    profile = CollectorProfile(
        user_id=current_user.id,
        specialization=payload.specialization,
        vehicle_type=payload.vehicle_type,
        is_active=True,
        rating=payload.rating or 0,
        total_collections=payload.total_collections or 0,
    )
    db.add(current_user)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.patch("/profile", response_model=CollectorProfileResponse)
def patch_collector_profile(payload: CollectorProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(CollectorProfile).filter(CollectorProfile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Collector profile not found")

    profile.specialization = payload.specialization
    profile.vehicle_type = payload.vehicle_type
    if payload.rating is not None:
        profile.rating = payload.rating
    if payload.total_collections is not None:
        profile.total_collections = payload.total_collections

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
