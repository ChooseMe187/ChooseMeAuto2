from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
from bson import ObjectId
import os
import requests
import logging
import csv
import io

from models.lead import (
    LeadCreate, LeadOut, LeadStatusUpdate, LegacyLeadCreate, Lead,
    NoteCreate, AssignmentUpdate, LeadNote
)
from auth import require_admin
from utils.alerts import notify_new_lead, notify_status_change

logger = logging.getLogger(__name__)

router = APIRouter()

# MongoDB connection - will be set in server.py
db = None

def set_db(database):
    global db
    db = database

def get_leads_collection():
    return db["leads"]


# Mailchimp configuration
MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_SERVER_PREFIX = os.getenv("MAILCHIMP_SERVER_PREFIX")
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID")


class FormLeadPayload(BaseModel):
    """Lead capture payload from frontend forms"""
    type: str  # "preapproval" | "test-drive" | "contact"
    firstName: str
    lastName: str
    phone: str
    email: EmailStr
    stockNumber: Optional[str] = None
    source: Optional[str] = None
    preferredDate: Optional[str] = None
    preferredTime: Optional[str] = None
    notes: Optional[str] = None
    message: Optional[str] = None


def serialize_lead(doc) -> dict:
    """Convert MongoDB document to LeadOut format"""
    # Parse notes
    notes = []
    for note in doc.get("notes", []):
        notes.append(LeadNote(
            at=note.get("at", datetime.now(timezone.utc)),
            by=note.get("by", "admin"),
            text=note.get("text", "")
        ))
    
    return {
        "id": str(doc["_id"]),
        "lead_type": doc.get("lead_type", "unknown"),
        "status": doc.get("status", "new"),
        "first_name": doc.get("first_name", ""),
        "last_name": doc.get("last_name"),
        "email": doc.get("email"),
        "phone": doc.get("phone"),
        "message": doc.get("message"),
        "vehicle_id": doc.get("vehicle_id"),
        "vin": doc.get("vin"),
        "stock_number": doc.get("stock_number"),
        "year": doc.get("year"),
        "make": doc.get("make"),
        "model": doc.get("model"),
        "trim": doc.get("trim"),
        "vehicle_summary": doc.get("vehicle_summary"),
        "contact_preference": doc.get("contact_preference"),
        "preferred_date": doc.get("preferred_date"),
        "preferred_time": doc.get("preferred_time"),
        "source_url": doc.get("source_url"),
        "source": doc.get("source"),
        # New fields
        "assigned_to": doc.get("assigned_to"),
        "notes": notes,
        "last_contacted_at": doc.get("last_contacted_at"),
        "created_at": doc.get("created_at", datetime.now(timezone.utc)),
        "updated_at": doc.get("updated_at", datetime.now(timezone.utc)),
    }


def map_form_type_to_lead_type(form_type: str) -> str:
    """Map form type strings to lead_type enum"""
    mapping = {
        "preapproval": "pre_approval",
        "pre-approval": "pre_approval",
        "test-drive": "test_drive",
        "testdrive": "test_drive",
        "contact": "contact",
        "availability": "availability",
    }
    return mapping.get(form_type.lower(), "contact")


def send_to_mailchimp(lead: FormLeadPayload):
    """Send lead data to Mailchimp audience."""
    if not all([MAILCHIMP_API_KEY, MAILCHIMP_SERVER_PREFIX, MAILCHIMP_LIST_ID]):
        return
    
    url = f"https://{MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members"
    
    merge_fields = {
        "FNAME": lead.firstName,
        "LNAME": lead.lastName,
    }
    
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
        "status": "subscribed",
        "merge_fields": merge_fields,
        "tags": [lead.type, lead.source or "unknown"]
    }
    
    try:
        response = requests.post(
            url,
            auth=("anystring", MAILCHIMP_API_KEY),
            json=data,
            timeout=10
        )
        if response.status_code in (200, 201):
            logger.info("✅ Lead sent to Mailchimp successfully")
        else:
            logger.warning(f"⚠️ Mailchimp API error: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Mailchimp error: {str(e)}")


# =============================================================================
# PUBLIC ENDPOINTS (Form submissions)
# =============================================================================

@router.post("/vehicle-leads")
async def create_form_lead(lead: FormLeadPayload):
    """
    Capture lead from any form (Pre-Approval, Test Drive, Contact).
    Saves to MongoDB and optionally sends to Mailchimp.
    """
    coll = get_leads_collection()
    now = datetime.now(timezone.utc)
    
    # Build document
    doc = {
        "lead_type": map_form_type_to_lead_type(lead.type),
        "status": "new",
        "first_name": lead.firstName,
        "last_name": lead.lastName,
        "email": lead.email,
        "phone": lead.phone,
        "stock_number": lead.stockNumber,
        "source": lead.source,
        "preferred_date": lead.preferredDate,
        "preferred_time": lead.preferredTime,
        "message": lead.notes or lead.message,
        "assigned_to": None,
        "notes": [],
        "last_contacted_at": None,
        "created_at": now,
        "updated_at": now,
    }
    
    # Save to MongoDB
    result = await coll.insert_one(doc)
    doc["_id"] = result.inserted_id
    
    logger.info(
        f"📩 New {lead.type} lead saved - ID: {result.inserted_id} | "
        f"Name: {lead.firstName} {lead.lastName} | Email: {lead.email}"
    )
    
    # Send to Mailchimp (async, don't block)
    try:
        send_to_mailchimp(lead)
    except Exception as e:
        logger.warning(f"⚠️ Mailchimp error: {str(e)}")
    
    # Send alerts
    try:
        notify_new_lead(doc)
    except Exception as e:
        logger.warning(f"⚠️ Alert error: {str(e)}")
    
    return {"ok": True, "message": "Lead captured successfully", "id": str(result.inserted_id)}


@router.post("/vehicle-leads/availability")
async def create_availability_lead(payload: LegacyLeadCreate):
    """
    Legacy endpoint for vehicle detail page 'Call For Availability' form.
    """
    coll = get_leads_collection()
    now = datetime.now(timezone.utc)
    
    # Parse name into first/last
    name_parts = payload.name.strip().split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    doc = {
        "lead_type": "availability",
        "status": "new",
        "first_name": first_name,
        "last_name": last_name,
        "email": payload.email,
        "phone": payload.phone,
        "contact_preference": payload.contact_preference,
        "message": payload.message,
        "stock_number": payload.stock_id,
        "vin": payload.vin,
        "vehicle_summary": payload.vehicle_summary,
        "source": "vehicle-detail-page",
        "assigned_to": None,
        "notes": [],
        "last_contacted_at": None,
        "created_at": now,
        "updated_at": now,
    }
    
    result = await coll.insert_one(doc)
    doc["_id"] = result.inserted_id
    
    logger.info(
        f"🚗 New availability lead - ID: {result.inserted_id} | "
        f"Stock: {payload.stock_id} | Customer: {payload.name}"
    )
    
    # Send alerts
    try:
        notify_new_lead(doc)
    except Exception as e:
        logger.warning(f"⚠️ Alert error: {str(e)}")
    
    # Return legacy format for backward compatibility
    return Lead(
        id=str(result.inserted_id),
        created_at=now,
        source="choose-me-auto-website",
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        contact_preference=payload.contact_preference,
        message=payload.message,
        stock_id=payload.stock_id,
        vin=payload.vin,
        vehicle_summary=payload.vehicle_summary,
    )


# =============================================================================
# ADMIN ENDPOINTS (Protected)
# =============================================================================

@router.get("/leads", response_model=List[LeadOut])
async def list_all_leads(
    status: Optional[str] = None,
    lead_type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    _: bool = Depends(require_admin)
):
    """List all leads (admin only)"""
    coll = get_leads_collection()
    
    query = {}
    if status:
        query["status"] = status
    if lead_type:
        query["lead_type"] = lead_type
    if assigned_to:
        query["assigned_to"] = assigned_to
    
    cursor = coll.find(query).sort("created_at", -1)
    docs = await cursor.to_list(500)
    
    return [serialize_lead(d) for d in docs]


@router.get("/leads/export.csv")
async def export_leads_csv(
    status: Optional[str] = None,
    lead_type: Optional[str] = None,
    _: bool = Depends(require_admin)
):
    """Export leads as CSV (admin only)"""
    coll = get_leads_collection()
    
    query = {}
    if status:
        query["status"] = status
    if lead_type:
        query["lead_type"] = lead_type
    
    docs = await coll.find(query).sort("created_at", -1).to_list(5000)
    
    def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow([
            "created_at", "lead_type", "status", "first_name", "last_name",
            "phone", "email", "year", "make", "model", "trim", "vin",
            "stock_number", "assigned_to", "notes_count", "source", "message"
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)
        
        # Data rows
        for d in docs:
            created = d.get("created_at")
            if created:
                created = created.strftime("%Y-%m-%d %H:%M:%S") if hasattr(created, 'strftime') else str(created)
            
            writer.writerow([
                created,
                d.get("lead_type"),
                d.get("status"),
                d.get("first_name"),
                d.get("last_name"),
                d.get("phone"),
                d.get("email"),
                d.get("year"),
                d.get("make"),
                d.get("model"),
                d.get("trim"),
                d.get("vin"),
                d.get("stock_number"),
                d.get("assigned_to"),
                len(d.get("notes", [])),
                d.get("source"),
                d.get("message", "")[:100] if d.get("message") else "",
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
    
    headers = {"Content-Disposition": "attachment; filename=choosemeauto-leads.csv"}
    return StreamingResponse(generate(), media_type="text/csv", headers=headers)


@router.get("/leads/stats/summary")
async def get_leads_stats(_: bool = Depends(require_admin)):
    """Get lead statistics (admin only)"""
    coll = get_leads_collection()
    
    total = await coll.count_documents({})
    new_count = await coll.count_documents({"status": "new"})
    
    # Count by type
    pipeline = [
        {"$group": {"_id": "$lead_type", "count": {"$sum": 1}}}
    ]
    type_counts = {}
    async for doc in coll.aggregate(pipeline):
        type_counts[doc["_id"] or "unknown"] = doc["count"]
    
    # Count by status
    status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_counts = {}
    async for doc in coll.aggregate(status_pipeline):
        status_counts[doc["_id"] or "unknown"] = doc["count"]
    
    return {
        "total": total,
        "new": new_count,
        "by_type": type_counts,
        "by_status": status_counts
    }


@router.get("/leads/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: str, _: bool = Depends(require_admin)):
    """Get a single lead by ID (admin only)"""
    coll = get_leads_collection()
    
    try:
        doc = await coll.find_one({"_id": ObjectId(lead_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid lead ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return serialize_lead(doc)


@router.patch("/leads/{lead_id}", response_model=LeadOut)
async def update_lead_status(
    lead_id: str,
    update: LeadStatusUpdate,
    _: bool = Depends(require_admin)
):
    """Update lead status (admin only)"""
    coll = get_leads_collection()
    
    try:
        doc = await coll.find_one({"_id": ObjectId(lead_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid lead ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    old_status = doc.get("status", "new")
    new_status = update.status
    
    update_fields = {
        "status": new_status,
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Update last_contacted_at if status is being changed to "contacted"
    if new_status == "contacted" and old_status != "contacted":
        update_fields["last_contacted_at"] = datetime.now(timezone.utc)
    
    await coll.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": update_fields}
    )
    
    updated = await coll.find_one({"_id": ObjectId(lead_id)})
    logger.info(f"📝 Lead {lead_id} status updated: {old_status} → {new_status}")
    
    # Send status change alert
    if old_status != new_status:
        try:
            notify_status_change(updated, old_status, new_status)
        except Exception as e:
            logger.warning(f"⚠️ Alert error: {str(e)}")
    
    return serialize_lead(updated)


@router.patch("/leads/{lead_id}/assign", response_model=LeadOut)
async def assign_lead(
    lead_id: str,
    assignment: AssignmentUpdate,
    _: bool = Depends(require_admin)
):
    """Assign a lead to a team member (admin only)"""
    coll = get_leads_collection()
    
    try:
        doc = await coll.find_one({"_id": ObjectId(lead_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid lead ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    await coll.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": {"assigned_to": assignment.assigned_to, "updated_at": datetime.now(timezone.utc)}}
    )
    
    updated = await coll.find_one({"_id": ObjectId(lead_id)})
    logger.info(f"👤 Lead {lead_id} assigned to: {assignment.assigned_to}")
    
    return serialize_lead(updated)


@router.post("/leads/{lead_id}/notes")
async def add_note(
    lead_id: str,
    note: NoteCreate,
    _: bool = Depends(require_admin)
):
    """Add a note to a lead (admin only)"""
    coll = get_leads_collection()
    
    try:
        doc = await coll.find_one({"_id": ObjectId(lead_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid lead ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    note_doc = {
        "at": datetime.now(timezone.utc),
        "by": note.by,
        "text": note.text
    }
    
    await coll.update_one(
        {"_id": ObjectId(lead_id)},
        {
            "$push": {"notes": note_doc},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    
    logger.info(f"📝 Note added to lead {lead_id} by {note.by}")
    
    return {"ok": True, "note": note_doc}


@router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, _: bool = Depends(require_admin)):
    """Delete a lead (admin only)"""
    coll = get_leads_collection()
    
    try:
        result = await coll.delete_one({"_id": ObjectId(lead_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid lead ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    logger.info(f"🗑️ Lead {lead_id} deleted")
    return {"message": "Lead deleted successfully"}


# Legacy endpoint for backward compatibility
@router.get("/vehicle-leads", response_model=List[LeadOut])
async def get_all_leads_legacy():
    """Legacy endpoint - returns all leads (public for now)"""
    coll = get_leads_collection()
    cursor = coll.find({}).sort("created_at", -1)
    docs = await cursor.to_list(100)
    return [serialize_lead(d) for d in docs]


@router.get("/vehicle-leads/count")
async def get_leads_count():
    """Get total count of leads"""
    coll = get_leads_collection()
    count = await coll.count_documents({})
    return {"count": count}
