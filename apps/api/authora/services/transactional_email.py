"""Transactional email for Authora.

Every message a customer needs in order to start, stay in, or get help is built
here and sent through the notification service (SMTP or SendGrid). Sending is
best-effort: a mail failure must never take down registration, checkout or a
support request, but it is always written to the app log so a gap is visible
instead of silent.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from html import escape

from authora.config import get_settings
from authora.infrastructure.notifications.factory import get_notification_service

logger = logging.getLogger(__name__)

BRAND = "Authora"
DEFAULT_SUPPORT_EMAIL = "support@authora.studio"


def support_email() -> str:
    return getattr(_settings(), "support_email", None) or DEFAULT_SUPPORT_EMAIL


def admin_email() -> str:
    return getattr(_settings(), "admin_email", None) or "admin@authora.studio"


def _settings():
    return get_settings()


def app_url(path: str = "") -> str:
    base = (_settings().app_base_url or "https://authora.studio").rstrip("/")
    if not path:
        return base
    return f"{base}/{path.lstrip('/')}"


def _layout(heading: str, body_html: str) -> str:
    return f"""<!doctype html>
<html><body style="margin:0;padding:0;background:#0d0f12;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0d0f12;padding:32px 16px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#14171c;border:1px solid #232830;border-radius:12px;overflow:hidden;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;">
        <tr><td style="padding:28px 32px 8px 32px;">
          <div style="font-size:12px;letter-spacing:3px;color:#c9a227;font-weight:700;">AUTHORA</div>
        </td></tr>
        <tr><td style="padding:8px 32px 0 32px;">
          <h1 style="margin:0;font-family:Georgia,serif;font-size:26px;line-height:1.25;color:#f5f2ea;font-weight:400;">{escape(heading)}</h1>
        </td></tr>
        <tr><td style="padding:18px 32px 28px 32px;color:#c3c7cf;font-size:15px;line-height:1.65;">
          {body_html}
        </td></tr>
        <tr><td style="padding:18px 32px 26px 32px;border-top:1px solid #232830;color:#7c828d;font-size:12px;line-height:1.6;">
          You are receiving this because you have an Authora account.<br>
          Need a human? Reply to this email or write to
          <a href="mailto:{support_email()}" style="color:#c9a227;text-decoration:none;">{support_email()}</a> — we answer within one business day.
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


def _button(label: str, href: str) -> str:
    return (
        f'<p style="margin:26px 0;"><a href="{escape(href)}" '
        'style="display:inline-block;background:#c9a227;color:#0d0f12;text-decoration:none;'
        'font-weight:700;padding:13px 22px;border-radius:8px;font-size:15px;">'
        f"{escape(label)}</a></p>"
    )


async def _send(to: str, subject: str, text: str, html: str) -> bool:
    if not to:
        return False
    try:
        service = get_notification_service()
        ok = await service.send_email(to, subject, text, html)
        if not ok:
            logger.warning("transactional email not sent (provider returned False): %s / %s", subject, to)
        return ok
    except Exception:  # noqa: BLE001 - email must never break the request
        logger.exception("transactional email failed: %s / %s", subject, to)
        return False


# --------------------------------------------------------------------------
# Welcome — sent the moment an account exists
# --------------------------------------------------------------------------
async def send_welcome(to: str, display_name: str | None = None) -> bool:
    name = (display_name or "").strip() or "there"
    subject = "Welcome to Authora — here is how to start your book"
    text = f"""Hi {name},

Your Authora account is ready. Everything below is in the app already; nothing else is required to begin.

1. Open your dashboard: {app_url('/dashboard')}
2. Choose Start a book. Pick a template, or begin from your own premise.
3. Answer the short brief — genre, audience, length. Authora turns that into a book idea, a Book Bible, an outline and chapter briefs.
4. Write in the editor. Autosave keeps a local copy as well as the saved version.
5. Export when you are ready: DOCX, EPUB, PDF, TXT, Markdown, HTML, JSON.
6. When the manuscript is finished, use Publish & release to send it to Anema House Publishing. You get a reference number back.

Your plan and billing live here: {app_url('/dashboard/billing')}
Common questions: {app_url('/help')}
Contact us: {app_url('/contact')} or {support_email()}

If anything is unclear, reply to this email and a person will answer.

— Authora
"""
    html = _layout(
        "Your book starts here",
        f"""<p style="margin:0 0 14px 0;">Hi {escape(name)},</p>
        <p style="margin:0 0 14px 0;">Your account is ready. Here is the whole path, start to finish — nothing else is needed to begin.</p>
        <ol style="margin:0 0 6px 18px;padding:0;">
          <li style="margin-bottom:8px;"><strong>Pick up your dashboard.</strong> Start a book, or choose a template.</li>
          <li style="margin-bottom:8px;"><strong>Answer the short brief.</strong> Genre, audience, length. Authora builds the idea, the Book Bible, the outline and the chapter briefs.</li>
          <li style="margin-bottom:8px;"><strong>Write.</strong> Autosave keeps a local copy as well as the saved version, so a dropped connection does not cost you words.</li>
          <li style="margin-bottom:8px;"><strong>Export.</strong> DOCX, EPUB, PDF, TXT, Markdown, HTML or JSON.</li>
          <li><strong>Publish.</strong> Publish &amp; release sends the finished manuscript to Anema House Publishing and returns a reference number.</li>
        </ol>
        {_button("Open my dashboard", app_url('/dashboard'))}
        <p style="margin:0 0 8px 0;">Questions: <a href="{escape(app_url('/help'))}" style="color:#c9a227;text-decoration:none;">the help centre</a> ·
        <a href="{escape(app_url('/contact'))}" style="color:#c9a227;text-decoration:none;">contact us</a> ·
        <a href="mailto:{support_email()}" style="color:#c9a227;text-decoration:none;">{support_email()}</a></p>
        <p style="margin:14px 0 0 0;color:#8b909a;font-size:13px;">A person reads every reply. If something is broken or missing, tell us and we will fix it.</p>""",
    )
    return await _send(to, subject, text, html)


# --------------------------------------------------------------------------
# Password reset
# --------------------------------------------------------------------------
async def send_password_reset(to: str, reset_url: str, display_name: str | None = None) -> bool:
    name = (display_name or "").strip() or "there"
    subject = "Reset your Authora password"
    text = f"""Hi {name},

Someone asked to reset the password for this Authora account. If that was you, open this link within the next hour:

{reset_url}

The link can be used once. If you did not ask for this, ignore this email — your password has not changed and nothing has happened to your account.

Need help? {support_email()}

— Authora
"""
    html = _layout(
        "Reset your password",
        f"""<p style="margin:0 0 14px 0;">Hi {escape(name)},</p>
        <p style="margin:0 0 4px 0;">Someone asked to reset the password for this account. If that was you, the link below works for the next hour and can be used once.</p>
        {_button("Choose a new password", reset_url)}
        <p style="margin:0 0 8px 0;color:#8b909a;font-size:13px;">If you did not ask for this, ignore this email. Your password has not changed.</p>
        <p style="margin:0;color:#8b909a;font-size:13px;">Link not working? Write to <a href="mailto:{support_email()}" style="color:#c9a227;text-decoration:none;">{support_email()}</a>.</p>""",
    )
    return await _send(to, subject, text, html)


# --------------------------------------------------------------------------
# Collaboration invite
# --------------------------------------------------------------------------
async def send_project_invite(
    to: str,
    *,
    inviter_name: str,
    project_title: str,
    role: str,
    invite_token: str,
    expires_at: datetime | None = None,
) -> bool:
    accept_url = app_url(f"/invite/{invite_token}")
    role_words = (role or "collaborator").replace("_", " ")
    subject = f"{inviter_name} invited you to {project_title} on Authora"
    when = ""
    if expires_at:
        when = f"\nThis invitation expires on {expires_at.strftime('%d %B %Y')}.\n"
    text = f"""{inviter_name} has invited you to work on "{project_title}" on Authora as a {role_words}.

Accept the invitation:
{accept_url}
{when}
You will be asked to sign in, or to create a free account, before the project opens. Creating an account takes about a minute and needs no payment details.

If you were not expecting this, ignore the email and nothing will happen.

Need help? {support_email()}
"""
    html = _layout(
        "You have been invited",
        f"""<p style="margin:0 0 14px 0;"><strong>{escape(inviter_name)}</strong> invited you to work on <strong>{escape(project_title)}</strong> as a {escape(role_words)}.</p>
        {_button("Accept the invitation", accept_url)}
        <p style="margin:0 0 8px 0;color:#8b909a;font-size:13px;">{escape(when.strip()) or 'Sign in, or create a free account, and the project opens.'}</p>
        <p style="margin:0;color:#8b909a;font-size:13px;">If you were not expecting this, ignore this email and nothing will happen.</p>""",
    )
    return await _send(to, subject, text, html)


# --------------------------------------------------------------------------
# Receipt
# --------------------------------------------------------------------------
async def send_receipt(
    to: str,
    *,
    description: str,
    amount_cents: int,
    currency: str = "usd",
    invoice_number: str | None = None,
    period_end: datetime | None = None,
) -> bool:
    amount = f"{amount_cents / 100:,.2f} {currency.upper()}"
    subject = f"Your Authora receipt — {amount}"
    renewed = f"\nYour access renews on {period_end.strftime('%d %B %Y')}." if period_end else ""
    text = f"""Thank you — your payment went through.

Item: {description}
Amount: {amount}
{f"Invoice: {invoice_number}" if invoice_number else ""}
Date: {datetime.now(timezone.utc).strftime('%d %B %Y')}
{renewed}

Manage your plan or download invoices: {app_url('/dashboard/billing')}

Questions about a charge? {support_email()} — we answer within one business day.

— Authora
"""
    html = _layout(
        "Payment received",
        f"""<p style="margin:0 0 16px 0;">Thank you — your payment went through.</p>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px;">
          <tr><td style="padding:9px 0;border-bottom:1px solid #232830;color:#8b909a;">Item</td><td align="right" style="padding:9px 0;border-bottom:1px solid #232830;color:#f5f2ea;">{escape(description)}</td></tr>
          <tr><td style="padding:9px 0;border-bottom:1px solid #232830;color:#8b909a;">Amount</td><td align="right" style="padding:9px 0;border-bottom:1px solid #232830;color:#f5f2ea;">{escape(amount)}</td></tr>
          {f'<tr><td style="padding:9px 0;border-bottom:1px solid #232830;color:#8b909a;">Invoice</td><td align="right" style="padding:9px 0;border-bottom:1px solid #232830;color:#f5f2ea;">{escape(invoice_number)}</td></tr>' if invoice_number else ''}
          <tr><td style="padding:9px 0;color:#8b909a;">Date</td><td align="right" style="padding:9px 0;color:#f5f2ea;">{datetime.now(timezone.utc).strftime('%d %B %Y')}</td></tr>
        </table>
        {_button("Manage billing", app_url('/dashboard/billing'))}
        <p style="margin:0;color:#8b909a;font-size:13px;">Questions about a charge? <a href="mailto:{support_email()}" style="color:#c9a227;text-decoration:none;">{support_email()}</a></p>""",
    )
    return await _send(to, subject, text, html)


# --------------------------------------------------------------------------
# Payment failed — the message that stops a silent churn
# --------------------------------------------------------------------------
async def send_payment_failed(to: str, *, retry_url: str | None = None) -> bool:
    subject = "Your Authora payment did not go through"
    link = retry_url or app_url("/dashboard/billing")
    text = f"""We could not take your last payment. Your account still works, and your work is untouched.

Your subscription has a short grace period. To keep access without interruption, update the card on file:
{link}

If nothing changes, the plan drops back to free at the end of the grace period — your books and exports remain yours and stay downloadable.

If you think this is a mistake, or you need more time, write to {support_email()} and we will sort it out.

— Authora
"""
    html = _layout(
        "That payment did not go through",
        f"""<p style="margin:0 0 14px 0;">We could not take your last payment. Your account still works, and your work is untouched.</p>
        <p style="margin:0 0 4px 0;">Update the card on file before the grace period ends and nothing interrupts.</p>
        {_button("Update payment details", link)}
        <p style="margin:0 0 8px 0;color:#8b909a;font-size:13px;">If nothing changes, the plan returns to free. Your books and exports stay yours and stay downloadable.</p>
        <p style="margin:0;color:#8b909a;font-size:13px;">Need more time? <a href="mailto:{support_email()}" style="color:#c9a227;text-decoration:none;">{support_email()}</a></p>""",
    )
    return await _send(to, subject, text, html)


# --------------------------------------------------------------------------
# Handover to Anema House Publishing
# --------------------------------------------------------------------------
async def send_submission_received(
    to: str,
    *,
    book_title: str,
    reference: str,
    house: str = "Anema House Publishing",
) -> bool:
    subject = f"{house} received “{book_title}” — reference {reference}"
    text = f"""Your manuscript has been delivered.

Book: {book_title}
Publisher: {house}
Reference: {reference}

Keep this reference. It is how you and the house identify your submission from here on.

What happens next:
- The house reads the pack you sent — manuscript, blurb, synopsis and any front matter.
- You can check the status any time from the book's Publish & release page in Authora.
- If the house needs anything else, they will contact you at this address.
- A decision usually arrives within four to six weeks. Silence is not a rejection; it means it is still in the queue.

Check status: {app_url('/dashboard/export')}
Questions about the submission: {support_email()}

— Authora
"""
    html = _layout(
        "Delivered to the house",
        f"""<p style="margin:0 0 14px 0;">Your manuscript has been delivered to <strong>{escape(house)}</strong>.</p>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px;">
          <tr><td style="padding:9px 0;border-bottom:1px solid #232830;color:#8b909a;">Book</td><td align="right" style="padding:9px 0;border-bottom:1px solid #232830;color:#f5f2ea;">{escape(book_title)}</td></tr>
          <tr><td style="padding:9px 0;color:#8b909a;">Reference</td><td align="right" style="padding:9px 0;color:#c9a227;font-weight:700;">{escape(reference)}</td></tr>
        </table>
        <p style="margin:16px 0 8px 0;">Keep this reference — it identifies your submission from here on. The house reads the pack you sent; a decision usually arrives within four to six weeks.</p>
        {_button("Check the submission", app_url('/dashboard/export'))}
        <p style="margin:0;color:#8b909a;font-size:13px;">Questions about the submission? <a href="mailto:{support_email()}" style="color:#c9a227;text-decoration:none;">{support_email()}</a></p>""",
    )
    return await _send(to, subject, text, html)


# --------------------------------------------------------------------------
# Contact form acknowledgement
# --------------------------------------------------------------------------
async def send_contact_ack(to: str, *, name: str | None, message: str) -> bool:
    subject = "We have your message — Authora support"
    text = f"""Hi {(name or 'there').strip()},

Your message reached us and a person will read it. We answer within one business day, usually sooner.

What you sent:
---
{message.strip()[:1200]}
---

If your question is about a book, include the book title in a reply and we will look at the actual project rather than guess.

— Authora support
{support_email()}
"""
    html = _layout(
        "We have your message",
        f"""<p style="margin:0 0 14px 0;">Hi {escape((name or 'there').strip())},</p>
        <p style="margin:0 0 14px 0;">Your message reached us and a person will read it. We answer within one business day, usually sooner.</p>
        <blockquote style="margin:0 0 14px 0;padding:12px 16px;border-left:3px solid #c9a227;background:#0d0f12;color:#a9aeb8;font-size:14px;white-space:pre-wrap;">{escape(message.strip()[:1200])}</blockquote>
        <p style="margin:0;color:#8b909a;font-size:13px;">If it is about a specific book, reply with the title and we will look at the project itself.</p>""",
    )
    return await _send(to, subject, text, html)


# --------------------------------------------------------------------------
# Support inbox — the other half of the contact form
# --------------------------------------------------------------------------
async def send_support_notification(
    *,
    from_email: str,
    name: str | None,
    lead_type: str,
    subject: str | None,
    message: str,
) -> bool:
    """Tell the support inbox that a human is waiting.

    The contact form used to write to a database table and stop there: no
    acknowledgement for the sender, no alert for us. A lead row nobody reads is
    a dropped support request.
    """
    subject_line = f"[Authora {lead_type}] {(subject or 'New message')[:90]}"
    text = f"""From: {name or 'Unknown'} <{from_email}>
Type: {lead_type}
Subject: {subject or '-'}

{message}

--
Reply directly to this email to answer the sender.
"""
    html = _layout(
        "New support message",
        f"""<p style="margin:0 0 14px 0;"><strong>{escape(name or 'Unknown')}</strong> &lt;{escape(from_email)}&gt;</p>
        <p style="margin:0 0 8px 0;color:#8b909a;font-size:13px;">Type: {escape(lead_type)} · Subject: {escape(subject or '-')}</p>
        <blockquote style="margin:14px 0;padding:12px 16px;border-left:3px solid #c9a227;background:#0d0f12;color:#d5d9e0;font-size:14px;white-space:pre-wrap;">{escape(message)}</blockquote>
        <p style="margin:0;color:#8b909a;font-size:13px;">Reply to this email to answer the sender directly.</p>""",
    )
    return await _send(admin_email(), subject_line, text, html)
