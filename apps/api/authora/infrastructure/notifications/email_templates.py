"""Email templates for reminder notifications.

Supportive, clean design. Never spammy.
"""


def reminder_email_html(title: str, body: str, product_name: str = "AUTHORA") -> str:
    """Generate HTML email for a reminder. Falls back to plain text if needed."""
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:16px;line-height:1.6;color:#333;background:#f5f5f5;">
  <div style="max-width:560px;margin:24px auto;padding:32px;background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
    <p style="margin:0 0 8px;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:0.05em;">{product_name}</p>
    <h1 style="margin:0 0 20px;font-size:20px;font-weight:600;color:#111;">{title}</h1>
    <p style="margin:0;color:#444;">{body}</p>
    <p style="margin:24px 0 0;font-size:13px;color:#888;">Your writing space is waiting. No pressure—just support.</p>
  </div>
</body>
</html>"""


def reminder_email_plain(title: str, body: str) -> str:
    """Plain text version (always used as fallback)."""
    return f"{title}\n\n{body}\n\n— Your writing space is waiting."
