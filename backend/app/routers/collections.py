from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import get_current_user, require_roles
from backend.app.models.collection_request import CollectionRequest
from backend.app.models.collector_profile import CollectorAssignment
from backend.app.models.user import User
from backend.app.models.waste_category import WasteCategory
from backend.app.models.waste_report import WasteReport
from backend.app.schemas.waste_management import CollectionRequestCreate, CollectionRequestResponse, CollectionRequestUpdate

router = APIRouter()
VALID_STATUS_TRANSITIONS = {
    "pending": {"assigned", "scheduled", "cancelled"},
    "assigned": {"scheduled", "in_progress", "cancelled"},
    "scheduled": {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


@router.get("/", response_model=list[CollectionRequestResponse])
def list_collections(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), status_filter: str | None = Query(None, alias="status")):
    query = db.query(CollectionRequest)
    if current_user.role == "citizen":
        query = query.filter(CollectionRequest.user_id == current_user.id)
    elif current_user.role == "collector":
        query = query.filter(CollectionRequest.assigned_collector_id == current_user.id)
    if status_filter:
        query = query.filter(CollectionRequest.status == status_filter)
    return query.offset(skip).limit(limit).all()


@router.get("/{collection_id}", response_model=CollectionRequestResponse)
def get_collection(collection_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    collection = db.query(CollectionRequest).filter(CollectionRequest.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection request not found")
    if current_user.role != "admin" and collection.user_id != current_user.id and collection.assigned_collector_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to view this collection")
    return collection


@router.post("/", response_model=CollectionRequestResponse)
def create_collection(payload: CollectionRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(WasteCategory).filter(WasteCategory.id == payload.category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Waste category not found")
    if payload.waste_report_id is not None:
        report = db.query(WasteReport).filter(WasteReport.id == payload.waste_report_id).first()
        if report is None:
            raise HTTPException(status_code=404, detail="Waste report not found")

    collection = CollectionRequest(
        request_id=f"CR-{uuid4().hex[:8].upper()}",
        title=payload.title,
        description=payload.description,
        location=payload.location,
        collection_date=payload.collection_date,
        status="pending",
        estimated_weight=payload.estimated_weight or 0.0,
        user_id=current_user.id,
        category_id=category.id,
        assigned_collector_id=None,
        waste_report_id=payload.waste_report_id,
        notes=payload.notes,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


@router.patch("/{collection_id}", response_model=CollectionRequestResponse)
def update_collection(collection_id: int, payload: CollectionRequestUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    collection = db.query(CollectionRequest).filter(CollectionRequest.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection request not found")
    if current_user.role != "admin" and collection.user_id != current_user.id and collection.assigned_collector_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to modify this collection")

    if payload.status is not None:
        if current_user.role not in {"admin", "collector"} and collection.user_id == current_user.id:
            raise HTTPException(status_code=403, detail="Only admin or assigned collector may update collection status")
        valid_next = VALID_STATUS_TRANSITIONS.get(collection.status, set())
        if payload.status not in valid_next and current_user.role != "admin":
            raise HTTPException(status_code=400, detail=f"Invalid status transition from {collection.status} to {payload.status}")
        collection.status = payload.status

    if payload.title is not None:
        collection.title = payload.title
    if payload.description is not None:
        collection.description = payload.description
    if payload.location is not None:
        collection.location = payload.location
    if payload.collection_date is not None:
        collection.collection_date = payload.collection_date
    if payload.estimated_weight is not None:
        collection.estimated_weight = payload.estimated_weight
    if payload.notes is not None:
        collection.notes = payload.notes
    if payload.assigned_collector_id is not None and current_user.role == "admin":
        collector = db.query(User).filter(User.id == payload.assigned_collector_id, User.role == "collector").first()
        if collector is None:
            raise HTTPException(status_code=400, detail="Assigned collector is invalid")
        collection.assigned_collector_id = collector.id
        collection.status = "assigned"

    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


@router.post("/{collection_id}/assign")
def assign_collector(collection_id: int, collector_id: int, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    collection = db.query(CollectionRequest).filter(CollectionRequest.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection request not found")
    collector = db.query(User).filter(User.id == collector_id, User.role == "collector").first()
    if collector is None:
        raise HTTPException(status_code=400, detail="Invalid collector selected")

    collection.assigned_collector_id = collector.id
    collection.status = "assigned"
    db.add(collection)
    db.add(
        CollectorAssignment(
            collection_request_id=collection.id,
            collector_id=collector.id,
            status="assigned",
            notes="Assigned by administrator",
        )
    )
    db.commit()
    return {"message": "Collector assigned successfully", "collection_id": collection.id, "collector_id": collector.id}


@router.delete("/{collection_id}")
def cancel_collection(collection_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    collection = db.query(CollectionRequest).filter(CollectionRequest.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection request not found")
    if current_user.role != "admin" and collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to cancel this collection")
    if collection.status in {"completed", "cancelled"}:
        raise HTTPException(status_code=400, detail="This collection cannot be cancelled in its current state")
    collection.status = "cancelled"
    db.add(collection)
    db.commit()
    return {"message": "Collection cancelled successfully"}
