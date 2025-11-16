from datetime import datetime
from typing import List
import uuid
import logging

from models.lead import LeadCreate, Lead

logger = logging.getLogger(__name__)

# Simple in-memory store for now
_LEADS: List[Lead] = []


def create_lead(data: LeadCreate) -> Lead:
    """
    Create a lead record.
    Currently stores in memory and logs; later you can:
      - Save to MongoDB
      - Send to CRM
      - Email BDC / sales desk
      - Trigger Twilio SMS/WhatsApp
    """
    lead = Lead(
        id=str(uuid.uuid4()),
        created_at=datetime.utcnow(),
        source="choose-me-auto-website",
        **data.dict(),
    )

    _LEADS.append(lead)

    logger.info(
        f"🚗 New vehicle lead captured - ID: {lead.id} | Stock: {lead.stock_id} | "
        f"Customer: {lead.name} | Phone: {lead.phone} | Email: {lead.email} | "
        f"Contact: {lead.contact_preference} | Vehicle: {lead.vehicle_summary}"
    )

    # 🔜 Hook points for future integrations:
    # - push_to_mongo(lead)
    # - send_email_notification(lead)
    # - trigger_twilio_sms(lead)
    # - push_to_crm(lead)

    return lead


def list_leads() -> List[Lead]:
    """Utility for testing – list all in-memory leads."""
    return list(_LEADS)


def get_lead_count() -> int:
    """Get total number of leads captured."""
    return len(_LEADS)
