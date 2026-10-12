from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import require_roles
from backend.app.models.collection_request import CollectionRequest
from backend.app.models.complaint import Complaint
from backend.app.models.user import User
from backend.app.models.waste_report import WasteReport
from backend.app.schemas.waste_management import AdminStatsResponse

router = APIRouter()


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    total_reports = db.query(WasteReport).count()
    pending_requests = db.query(CollectionRequest).filter(CollectionRequest.status == "pending").count()
    completed_collections = db.query(CollectionRequest).filter(CollectionRequest.status == "completed").count()
    unresolved_complaints = db.query(Complaint).filter(Complaint.status != "resolved").count()
    waste_collected_kg = float(
        db.query(func.coalesce(func.sum(CollectionRequest.actual_weight), 0))
        .filter(CollectionRequest.status == "completed")
        .scalar()
        or 0
    )
    return {
        "total_reports": total_reports,
        "pending_requests": pending_requests,
        "completed_collections": completed_collections,
        "unresolved_complaints": unresolved_complaints,
        "waste_collected_kg": waste_collected_kg,
    }
