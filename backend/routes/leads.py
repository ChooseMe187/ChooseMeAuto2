from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from models.lead import LeadCreate, Lead
from services.lead_service import create_lead, list_leads, get_lead_count
import os
import requests

router = APIRouter()

# Mailchimp configuration from environment variables
MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_SERVER_PREFIX = os.getenv("MAILCHIMP_SERVER_PREFIX")  # e.g. "us21"
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID")  # your audience ID


class FormLeadPayload(BaseModel):
    """Lead capture payload from frontend forms (Pre-Approval, Test Drive, Contact)"""
    type: str  # "preapproval" | "test-drive" | "contact"
    firstName: str
    lastName: str
    phone: str
    email: EmailStr
    stockNumber: Optional[str] = None
    source: Optional[str] = None
    
    # Test Drive specific fields
    preferredDate: Optional[str] = None
    preferredTime: Optional[str] = None
    notes: Optional[str] = None
    
    # Contact form specific field
    message: Optional[str] = None


def send_to_mailchimp(lead: FormLeadPayload):
    """
    Send lead data to Mailchimp audience.
    Raises exception if Mailchimp API fails.
    """
    url = f"https://{MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members"
    
    # Build merge fields for Mailchimp
    # Note: These custom fields must exist in your Mailchimp audience
    merge_fields = {
        "FNAME": lead.firstName,
        "LNAME": lead.lastName,
    }
    
    # Add custom fields if they exist in your Mailchimp setup
    if lead.phone:
        merge_fields["PHONE"] = lead.phone
    if lead.stockNumber:
        merge_fields["STOCK"] = lead.stockNumber
    if lead.source:
        merge_fields["SOURCE"] = lead.source
    if lead.type:
        merge_fields["LEADTYPE"] = lead.type
    
    data = {
        "email_address": lead.email,
        "status": "subscribed",  # or "pending" for double opt-in
        "merge_fields": merge_fields,
        "tags": [lead.type, lead.source or "unknown"]  # Tag leads for segmentation
    }
    
    response = requests.post(
        url,
        auth=("anystring", MAILCHIMP_API_KEY),
        json=data,
        timeout=10
    )
    
    if response.status_code not in (200, 201):
        error_detail = response.text
        print(f"❌ Mailchimp API error: {response.status_code} - {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add lead to Mailchimp: {error_detail}"
        )
    
    print(f"✅ Lead sent to Mailchimp successfully")


@router.post("/vehicle-leads")
def create_form_lead(lead: FormLeadPayload):
    """
    Capture lead from any form (Pre-Approval, Test Drive, Contact).
    Optionally sends to Mailchimp if configured.
    
    This is the NEW endpoint for the updated form pages.
    """
    
    # Log the lead
    print(f"📩 New {lead.type} lead received:")
    print(f"   Name: {lead.firstName} {lead.lastName}")
    print(f"   Email: {lead.email}")
    print(f"   Phone: {lead.phone}")
    print(f"   Stock: {lead.stockNumber or 'N/A'}")
    print(f"   Source: {lead.source}")
    
    # Optional: Push to Mailchimp if credentials are configured
    if MAILCHIMP_API_KEY and MAILCHIMP_SERVER_PREFIX and MAILCHIMP_LIST_ID:
        try:
            send_to_mailchimp(lead)
        except Exception as e:
            # Don't fail the request if Mailchimp fails
            print(f"⚠️ Mailchimp error: {str(e)}")
    else:
        print("ℹ️ Mailchimp not configured - skipping email list sync")
    
    # TODO: Save to MongoDB here if needed in the future
    # For now, just log and send to Mailchimp
    
    return {"ok": True, "message": "Lead captured successfully"}


@router.post("/vehicle-leads/availability", response_model=Lead, status_code=status.HTTP_201_CREATED)
def create_vehicle_lead(payload: LeadCreate):
    """
    LEGACY ENDPOINT: Capture a 'Call For Availability & Price' lead from the website.
    This is the original endpoint for the vehicle detail page lead form.

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
