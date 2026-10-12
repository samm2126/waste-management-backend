from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import get_current_user, require_roles
from backend.app.models.user import User
from backend.app.models.recycling_center import RecyclingCenter, RecyclingCenterCategory
from backend.app.models.waste_category import WasteCategory
from backend.app.schemas.waste_management import RecyclingCenterCreate, RecyclingCenterResponse

router = APIRouter()


@router.get("/", response_model=list[RecyclingCenterResponse])
def list_recycling_centers(db: Session = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), city: str | None = None):
    query = db.query(RecyclingCenter)
    if city:
        query = query.filter(RecyclingCenter.city.ilike(f"%{city}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{center_id}", response_model=RecyclingCenterResponse)
def get_recycling_center(center_id: int, db: Session = Depends(get_db)):
    center = db.query(RecyclingCenter).filter(RecyclingCenter.id == center_id).first()
    if center is None:
        raise HTTPException(status_code=404, detail="Recycling center not found")
    return center


@router.post("/", response_model=RecyclingCenterResponse)
def create_recycling_center(payload: RecyclingCenterCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    if not payload.category_ids:
        raise HTTPException(status_code=400, detail="At least one accepted waste category is required")

    center = RecyclingCenter(
        name=payload.name,
        address=payload.address,
        city=payload.city,
        phone=payload.phone,
        email=payload.email,
        operating_hours=payload.operating_hours,
        website=payload.website,
        is_active="active",
    )
    db.add(center)
    db.commit()
    db.refresh(center)

    for category_id in payload.category_ids:
        category = db.query(WasteCategory).filter(WasteCategory.id == category_id).first()
        if category is None:
            raise HTTPException(status_code=404, detail=f"Waste category with id {category_id} not found")
        db.add(RecyclingCenterCategory(center_id=center.id, category_id=category.id))

    db.commit()
    return center
