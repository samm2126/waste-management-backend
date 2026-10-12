from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WasteCategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category_type: str = Field(..., min_length=2, max_length=50)
    description: str | None = None
    is_recyclable: bool = False
    is_organic: bool = False
    is_hazardous: bool = False


class WasteCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category_type: str
    description: str | None = None
    is_recyclable: bool
    is_organic: bool
    is_hazardous: bool
    is_active: bool
    created_at: datetime


class WasteReportCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=10)
    location: str = Field(..., min_length=2, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    report_date: datetime | None = None
    image_url: str | None = None
    category_id: int


class WasteReportUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str | None = None
    image_url: str | None = None


class WasteReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_id: str
    title: str
    description: str
    location: str
    latitude: float | None = None
    longitude: float | None = None
    image_url: str | None = None
    status: str
    category_id: int
    user_id: int
    report_date: datetime
    created_at: datetime


class CollectionRequestCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    location: str = Field(..., min_length=2, max_length=255)
    collection_date: datetime
    category_id: int
    estimated_weight: float | None = 0.0
    notes: str | None = None
    waste_report_id: int | None = None


class CollectionRequestUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    collection_date: datetime | None = None
    status: str | None = None
    estimated_weight: float | None = None
    notes: str | None = None
    assigned_collector_id: int | None = None


class CollectionRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: str
    title: str
    description: str | None = None
    location: str
    collection_date: datetime
    status: str
    estimated_weight: float
    actual_weight: float | None = None
    user_id: int
    category_id: int
    assigned_collector_id: int | None = None
    waste_report_id: int | None = None
    notes: str | None = None
    created_at: datetime


class CollectorProfileCreate(BaseModel):
    specialization: str = Field(..., min_length=2, max_length=255)
    vehicle_type: str | None = None
    rating: int | None = 0
    total_collections: int | None = 0


class CollectorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    specialization: str
    vehicle_type: str | None = None
    is_active: bool
    rating: int
    total_collections: int


class RecyclingCenterCreate(BaseModel):
    name: str
    address: str
    city: str
    phone: str | None = None
    email: str | None = None
    operating_hours: str | None = None
    website: str | None = None
    category_ids: list[int] = []


class RecyclingCenterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    city: str
    phone: str | None = None
    email: str | None = None
    operating_hours: str | None = None
    website: str | None = None
    is_active: str


class ComplaintCreate(BaseModel):
    complaint_type: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10)
    location: str = Field(..., min_length=2, max_length=255)


class ComplaintUpdate(BaseModel):
    complaint_type: str | None = None
    description: str | None = None
    location: str | None = None
    status: str | None = None


class ComplaintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_id: str
    user_id: int
    complaint_type: str
    description: str
    location: str
    status: str
    created_at: datetime


class FeedbackCreate(BaseModel):
    collection_request_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    collection_request_id: int
    rating: int
    comment: str | None = None
    created_at: datetime


class AdminStatsResponse(BaseModel):
    total_reports: int
    pending_requests: int
    completed_collections: int
    unresolved_complaints: int
    waste_collected_kg: float
