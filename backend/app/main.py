from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import Base, engine
from backend.app.routers import admin, auth, collections, collectors, complaints, feedback, recycling_centers, users, waste_categories, waste_reports

app = FastAPI(title="Waste Management API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(waste_reports.router, prefix="/api/v1/waste-reports", tags=["Waste Reports"])
app.include_router(collections.router, prefix="/api/v1/collections", tags=["Collections"])
app.include_router(collectors.router, prefix="/api/v1/collectors", tags=["Collectors"])
app.include_router(waste_categories.router, prefix="/api/v1/waste-categories", tags=["Waste Categories"])
app.include_router(recycling_centers.router, prefix="/api/v1/recycling-centers", tags=["Recycling Centers"])
app.include_router(complaints.router, prefix="/api/v1/complaints", tags=["Complaints"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Feedback"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Waste Management API is running"}
