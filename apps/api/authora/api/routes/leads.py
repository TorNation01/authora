"""Marketing lead capture - newsletter, waitlist, demo requests."""

import uuid

from fastapi import APIRouter
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
async def create_lead(body: LeadCreate):
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

    return {"success": True, "id": lead_id}
