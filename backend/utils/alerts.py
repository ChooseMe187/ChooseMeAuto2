"""
Alert notifications module for Choose Me Auto

Phase 2B Status:
- Phase 2B.1 – Email Architecture: ✅ Complete
- Phase 2B.2 – Email Provider Activation: ⏸ Deferred (external dependency)

When provider credentials are added, simply update backend/.env with:
- ALERTS_ENABLED=true
- SMTP_HOST, SMTP_USER, SMTP_PASS, ALERT_EMAIL_TO (for email)
- TWILIO_* vars (for SMS)
- SLACK_WEBHOOK_URL (for Slack)
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple
import httpx

logger = logging.getLogger(__name__)

# Alert settings from environment
ALERTS_ENABLED = os.getenv("ALERTS_ENABLED", "false").lower() == "true"
ALERT_ON_NEW_LEAD = os.getenv("ALERT_ON_NEW_LEAD", "true").lower() == "true"
ALERT_ON_STATUS_CHANGE = os.getenv("ALERT_ON_STATUS_CHANGE", "true").lower() == "true"

# Email settings
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", SMTP_USER)

# Twilio settings
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM", "")
ALERT_SMS_TO = os.getenv("ALERT_SMS_TO", "")

# Slack settings
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def get_notification_status() -> dict:
    """Get the current status of all notification channels"""
    return {
        "alerts_enabled": ALERTS_ENABLED,
        "email": {
            "configured": all([SMTP_HOST, SMTP_USER, SMTP_PASS, ALERT_EMAIL_TO]),
            "status": "active" if all([SMTP_HOST, SMTP_USER, SMTP_PASS, ALERT_EMAIL_TO]) else "deferred"
        },
        "sms": {
            "configured": all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, ALERT_SMS_TO]),
            "status": "active" if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, ALERT_SMS_TO]) else "deferred"
        },
        "slack": {
            "configured": bool(SLACK_WEBHOOK_URL),
            "status": "active" if SLACK_WEBHOOK_URL else "deferred"
        }
    }


def format_lead_type(lead_type: str) -> str:
    """Format lead type for display"""
    mapping = {
        "pre_approval": "Pre-Approval",
        "test_drive": "Test Drive",
        "contact": "Contact",
        "availability": "Availability",
    }
    return mapping.get(lead_type, lead_type)


def format_lead_message(lead: dict, event_type: str = "new") -> Tuple[str, str]:
    """Format lead data for alert message. Returns (subject, body)"""
    lead_type = format_lead_type(lead.get("lead_type", "unknown"))
    first_name = lead.get("first_name", "Unknown")
    last_name = lead.get("last_name", "")
    name_initial = f"{first_name} {last_name[0]}." if last_name else first_name
    
    # Build vehicle info
    vehicle_parts = []
    if lead.get("year"):
        vehicle_parts.append(str(lead["year"]))
    if lead.get("make"):
        vehicle_parts.append(lead["make"])
    if lead.get("model"):
        vehicle_parts.append(lead["model"])
    vehicle_info = " ".join(vehicle_parts) if vehicle_parts else lead.get("vehicle_summary", "")
    
    if event_type == "new":
        subject = f"🚗 New {lead_type} Lead — {name_initial}"
        if vehicle_info:
            subject += f" — {vehicle_info}"
    else:
        status = lead.get("status", "unknown")
        subject = f"📝 Lead Status Changed — {name_initial} → {status.upper()}"
    
    # Build body
    body_lines = [
        f"{'='*50}",
        f"Lead Type: {lead_type}",
        f"Status: {lead.get('status', 'new').upper()}",
        f"",
        f"👤 Customer Info:",
        f"   Name: {first_name} {last_name}",
        f"   Phone: {lead.get('phone', 'N/A')}",
        f"   Email: {lead.get('email', 'N/A')}",
    ]
    
    if lead.get("contact_preference"):
        body_lines.append(f"   Preferred Contact: {lead['contact_preference']}")
    
    if vehicle_info or lead.get("stock_number") or lead.get("vin"):
        body_lines.append(f"")
        body_lines.append(f"🚗 Vehicle Info:")
        if vehicle_info:
            body_lines.append(f"   Vehicle: {vehicle_info}")
        if lead.get("stock_number"):
            body_lines.append(f"   Stock #: {lead['stock_number']}")
        if lead.get("vin"):
            body_lines.append(f"   VIN: {lead['vin']}")
    
    if lead.get("preferred_date") or lead.get("preferred_time"):
        body_lines.append(f"")
        body_lines.append(f"📅 Appointment:")
        if lead.get("preferred_date"):
            body_lines.append(f"   Date: {lead['preferred_date']}")
        if lead.get("preferred_time"):
            body_lines.append(f"   Time: {lead['preferred_time']}")
    
    if lead.get("message"):
        body_lines.append(f"")
        body_lines.append(f"💬 Message:")
        body_lines.append(f"   {lead['message']}")
    
    if lead.get("source_url"):
        body_lines.append(f"")
        body_lines.append(f"🔗 Source: {lead['source_url']}")
    
    body_lines.append(f"")
    body_lines.append(f"{'='*50}")
    body_lines.append(f"Choose Me Auto - Admin Panel")
    
    body = "\n".join(body_lines)
    return subject, body


def send_email(subject: str, body: str) -> dict:
    """
    Send email notification
    Returns: {"sent": bool, "status": "sent"|"deferred"|"error", "message": str}
    """
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, ALERT_EMAIL_TO]):
        logger.info(f"📧 [EMAIL DEFERRED] Provider not configured - Subject: {subject[:50]}...")
        return {"sent": False, "status": "deferred", "message": "Email provider not configured"}
    
    try:
        msg = MIMEMultipart()
        msg["From"] = ALERT_EMAIL_FROM
        msg["To"] = ALERT_EMAIL_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(ALERT_EMAIL_FROM, ALERT_EMAIL_TO.split(","), msg.as_string())
        
        logger.info(f"📧 [EMAIL SENT] {subject}")
        return {"sent": True, "status": "sent", "message": "Email sent successfully"}
    except Exception as e:
        logger.error(f"📧 [EMAIL ERROR] {subject} - {e}")
        return {"sent": False, "status": "error", "message": str(e)}


def send_sms(body: str) -> dict:
    """
    Send SMS notification via Twilio
    Returns: {"sent": bool, "status": "sent"|"deferred"|"error", "message": str}
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, ALERT_SMS_TO]):
        logger.info(f"📱 [SMS DEFERRED] Provider not configured")
        return {"sent": False, "status": "deferred", "message": "SMS provider not configured"}
    
    try:
        # Truncate body for SMS (160 char limit for single SMS)
        sms_body = body[:300] + "..." if len(body) > 300 else body
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        
        with httpx.Client() as client:
            response = client.post(
                url,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                data={
                    "From": TWILIO_FROM,
                    "To": ALERT_SMS_TO,
                    "Body": sms_body,
                },
                timeout=10,
            )
            
            if response.status_code in (200, 201):
                logger.info(f"📱 [SMS SENT]")
                return {"sent": True, "status": "sent", "message": "SMS sent successfully"}
            else:
                logger.error(f"📱 [SMS ERROR] {response.text}")
                return {"sent": False, "status": "error", "message": response.text}
    except Exception as e:
        logger.error(f"📱 [SMS ERROR] {e}")
        return {"sent": False, "status": "error", "message": str(e)}


def send_slack(subject: str, body: str) -> dict:
    """
    Send Slack notification
    Returns: {"sent": bool, "status": "sent"|"deferred"|"error", "message": str}
    """
    if not SLACK_WEBHOOK_URL:
        logger.info(f"💬 [SLACK DEFERRED] Webhook not configured - Subject: {subject[:50]}...")
        return {"sent": False, "status": "deferred", "message": "Slack webhook not configured"}
    
    try:
        payload = {
            "text": subject,
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": subject, "emoji": True}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"```{body}```"}
                }
            ]
        }
        
        with httpx.Client() as client:
            response = client.post(
                SLACK_WEBHOOK_URL,
                json=payload,
                timeout=10,
            )
            
            if response.status_code == 200:
                logger.info(f"💬 [SLACK SENT] {subject}")
                return {"sent": True, "status": "sent", "message": "Slack message sent"}
            else:
                logger.error(f"💬 [SLACK ERROR] {response.text}")
                return {"sent": False, "status": "error", "message": response.text}
    except Exception as e:
        logger.error(f"💬 [SLACK ERROR] {e}")
        return {"sent": False, "status": "error", "message": str(e)}


def notify_new_lead(lead: dict) -> dict:
    """
    Send notifications for a new lead
    Returns: {"notified": bool, "channels": {...}, "email_status": "sent"|"deferred"|"error"|"disabled"}
    """
    result = {
        "notified": False,
        "channels": {},
        "email_status": "disabled"
    }
    
    if not ALERTS_ENABLED:
        logger.info(f"🔔 [ALERTS DISABLED] New lead received - ID: {lead.get('id', 'unknown')}")
        return result
    
    if not ALERT_ON_NEW_LEAD:
        logger.info(f"🔔 [NEW LEAD ALERTS DISABLED] Lead ID: {lead.get('id', 'unknown')}")
        return result
    
    subject, body = format_lead_message(lead, "new")
    
    # Send via all configured channels
    result["channels"]["email"] = send_email(subject, body)
    result["channels"]["sms"] = send_sms(f"{subject}\n\nPhone: {lead.get('phone', 'N/A')}\nEmail: {lead.get('email', 'N/A')}")
    result["channels"]["slack"] = send_slack(subject, body)
    
    # Set overall status
    result["notified"] = any(ch.get("sent") for ch in result["channels"].values())
    result["email_status"] = result["channels"]["email"]["status"]
    
    return result


def notify_status_change(lead: dict, old_status: str, new_status: str) -> dict:
    """
    Send notifications for a status change
    Returns: {"notified": bool, "channels": {...}, "email_status": "sent"|"deferred"|"error"|"disabled"}
    """
    result = {
        "notified": False,
        "channels": {},
        "email_status": "disabled"
    }
    
    if not ALERTS_ENABLED:
        logger.info(f"🔔 [ALERTS DISABLED] Status change: {old_status} → {new_status}")
        return result
    
    if not ALERT_ON_STATUS_CHANGE:
        logger.info(f"🔔 [STATUS ALERTS DISABLED] {old_status} → {new_status}")
        return result
    
    subject, body = format_lead_message(lead, "status_change")
    extra_info = f"\n\nStatus changed: {old_status.upper()} → {new_status.upper()}"
    
    # Send via all configured channels
    result["channels"]["email"] = send_email(subject, body + extra_info)
    result["channels"]["sms"] = send_sms(f"{subject}\n{old_status} → {new_status}")
    result["channels"]["slack"] = send_slack(subject, body + extra_info)
    
    # Set overall status
    result["notified"] = any(ch.get("sent") for ch in result["channels"].values())
    result["email_status"] = result["channels"]["email"]["status"]
    
    return result
