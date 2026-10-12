from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.waste_category import WasteCategory
from backend.app.models.waste_report import WasteReport
from backend.app.schemas.waste_management import WasteReportCreate, WasteReportResponse, WasteReportUpdate

router = APIRouter()


@router.get("/", response_model=list[WasteReportResponse])
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), status_filter: str | None = Query(None, alias="status"), category_id: int | None = None):
    query = db.query(WasteReport)
    if current_user.role != "admin":
        query = query.filter(WasteReport.user_id == current_user.id)
    if status_filter:
        query = query.filter(WasteReport.status == status_filter)
    if category_id:
        query = query.filter(WasteReport.category_id == category_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{report_id}", response_model=WasteReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(WasteReport).filter(WasteReport.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Waste report not found")
    if current_user.role != "admin" and report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to view this report")
    return report


@router.post("/", response_model=WasteReportResponse)
def create_report(payload: WasteReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(WasteCategory).filter(WasteCategory.id == payload.category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Waste category not found")

    report = WasteReport(
        report_id=f"WR-{uuid4().hex[:8].upper()}",
        title=payload.title,
        description=payload.description,
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        report_date=payload.report_date or datetime.utcnow(),
        image_url=payload.image_url,
        status="submitted",
        user_id=current_user.id,
        category_id=category.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.patch("/{report_id}", response_model=WasteReportResponse)
def update_report(report_id: int, payload: WasteReportUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(WasteReport).filter(WasteReport.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Waste report not found")
    if current_user.role != "admin" and report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to update this report")

    if payload.title is not None:
        report.title = payload.title
    if payload.description is not None:
        report.description = payload.description
    if payload.location is not None:
        report.location = payload.location
    if payload.latitude is not None:
        report.latitude = payload.latitude
    if payload.longitude is not None:
        report.longitude = payload.longitude
    if payload.status is not None and current_user.role == "admin":
        report.status = payload.status
    if payload.image_url is not None:
        report.image_url = payload.image_url

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(WasteReport).filter(WasteReport.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Waste report not found")
    if current_user.role != "admin" and report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can not delete this report")
    if report.status in {"in_progress", "completed", "cancelled"}:
        raise HTTPException(status_code=400, detail="This report cannot be deleted in its current state")
    db.delete(report)
    db.commit()
    return {"message": "Waste report deleted successfully"}
