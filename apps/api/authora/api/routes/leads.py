"""Marketing lead capture - newsletter, waitlist, demo requests."""

import uuid

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field

from authora.database import async_session_factory
from sqlalchemy import text

router = APIRouter(prefix="/leads", tags=["leads"])


class LeadCreate(BaseModel):
    model_config = {"populate_by_name": True}

    email: EmailStr
    type: str = "newsletter"
    name: str | None = None
    company: str | None = None
    message: str | None = None
    subject: str | None = None
    use_case: str | None = Field(None, alias="useCase")


@router.post("", status_code=201)
async def create_lead(body: LeadCreate, background: BackgroundTasks):
    """Capture a lead (newsletter, contact, demo request). No auth required."""
    lead_id = str(uuid.uuid4())
    email = body.email.strip().lower()
    lead_type = (body.type or "newsletter").strip() or "newsletter"
    name = body.name.strip() if body.name else None
    company = body.company.strip() if body.company else None
    message = body.message.strip() if body.message else None
    subject = body.subject.strip() if body.subject else None
    use_case = body.use_case.strip() if body.use_case else None

    async with async_session_factory() as db:
        await db.execute(
            text("""
                INSERT INTO leads (id, email, type, name, company, message, subject, use_case)
                VALUES (:id, :email, :type, :name, :company, :message, :subject, :use_case)
            """),
            {
                "id": lead_id,
                "email": email,
                "type": lead_type,
                "name": name,
                "company": company,
                "message": message,
                "subject": subject,
                "use_case": use_case,
            },
        )
        await db.commit()

    # Answer the sender, and alert the support inbox. Both are queued after the
    # row is stored so a mail problem never loses the request itself.
    from authora.services.transactional_email import (
        send_contact_ack,
        send_support_notification,
    )

    if lead_type in ("contact", "support", "demo"):
        background.add_task(send_contact_ack, email, name=name, message=message or subject or "(no message)")
        background.add_task(
            send_support_notification,
            from_email=email,
            name=name,
            lead_type=lead_type,
            subject=subject,
            message=message or "(no message body)",
        )

    return {"success": True, "id": lead_id}
