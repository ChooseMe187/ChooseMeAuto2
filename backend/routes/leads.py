from fastapi import APIRouter, HTTPException, status
from typing import List
from models.lead import LeadCreate, Lead
from services.lead_service import create_lead, list_leads, get_lead_count

router = APIRouter()


@router.post("/vehicle-leads", response_model=Lead, status_code=status.HTTP_201_CREATED)
def create_vehicle_lead(payload: LeadCreate):
    """
    Capture a 'Call For Availability & Price' lead from the website.

    Expected JSON body (matches your React form):
    {
      "name": "Customer Name",
      "phone": "555-555-5555",
      "email": "test@example.com",
      "contact_preference": "text",
      "message": "Optional notes from customer",
      "stock_id": "P57801",
      "vin": "1G1ZD5ST6NF127154",
      "vehicle_summary": "2022 Chevrolet Malibu LT"
    }
    """
    try:
        lead = create_lead(payload)
        return lead
    except Exception as e:
        # Keep it simple; you can customize error logging later
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lead",
        ) from e


@router.get("/vehicle-leads", response_model=List[Lead])
def get_all_leads():
    """
    Debug endpoint to view all captured leads.
    Useful for testing and internal dashboards.
    """
    return list_leads()


@router.get("/vehicle-leads/count")
def get_leads_count():
    """
    Get total count of captured leads.
    """
    return {"count": get_lead_count()}
