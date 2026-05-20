# backend/app/routes/admin_routes.py

from fastapi import APIRouter
from app.services.lead_service import LeadService

router = APIRouter()

# ---------------------------------------------------
# Health Check
# ---------------------------------------------------
@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Suraj AI Chat Framework backend running"
    }

# ---------------------------------------------------
# Get all leads (for admin preview)
# ---------------------------------------------------
@router.get("/leads")
async def get_leads():
    leads = LeadService.get_all_leads()
    return {
        "count": len(leads),
        "data": leads
    }

# ---------------------------------------------------
# Quick test API
# ---------------------------------------------------
@router.get("/test")
async def test_api():
    return {
        "message": "Admin route working successfully"
    }