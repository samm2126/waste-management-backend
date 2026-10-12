from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import get_current_user, require_roles
from backend.app.models.user import User
from backend.app.models.waste_category import WasteCategory
from backend.app.schemas.waste_management import WasteCategoryCreate, WasteCategoryResponse

router = APIRouter()


@router.get("/", response_model=list[WasteCategoryResponse])
def list_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    return db.query(WasteCategory).filter(WasteCategory.is_active.is_(True)).offset(skip).limit(limit).all()


@router.get("/{category_id}", response_model=WasteCategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    category = db.query(WasteCategory).filter(WasteCategory.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Waste category not found")
    return category


@router.post("/", response_model=WasteCategoryResponse)
def create_category(payload: WasteCategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    existing = db.query(WasteCategory).filter(WasteCategory.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Waste category already exists")

    category = WasteCategory(
        name=payload.name,
        category_type=payload.category_type,
        description=payload.description,
        is_recyclable=payload.is_recyclable,
        is_organic=payload.is_organic,
        is_hazardous=payload.is_hazardous,
        is_active=True,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=WasteCategoryResponse)
def update_category(category_id: int, payload: WasteCategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    category = db.query(WasteCategory).filter(WasteCategory.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Waste category not found")

    category.name = payload.name
    category.category_type = payload.category_type
    category.description = payload.description
    category.is_recyclable = payload.is_recyclable
    category.is_organic = payload.is_organic
    category.is_hazardous = payload.is_hazardous
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    category = db.query(WasteCategory).filter(WasteCategory.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Waste category not found")
    category.is_active = False
    db.add(category)
    db.commit()
    return {"message": "Waste category disabled successfully"}
