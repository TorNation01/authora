"""Email templates for reminder notifications.

Brand-matched to the Authora product: orange #FF6A2B, cream #FAF9F7, Inter.
Supportive, clean design. Never spammy.
"""

_ORANGE = "#FF6A2B"
_ORANGE_DEEP = "#E2551B"
_CREAM = "#F6F2EC"
_CREAM_SOFT = "#FAF9F7"
_INK = "#1A1A1A"
_BODY = "#403A34"
_MUTED = "#8C857D"
_BORDER = "#E6E0D8"
_FONT = (
    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "'Helvetica Neue', Arial, sans-serif"
)


def reminder_email_html(title: str, body: str, product_name: str = "AUTHORA") -> str:
    """Generate HTML email for a reminder. Falls back to plain text if needed."""
    return f"""<!DOCTYPE html>
<html lang="en" style="color-scheme:light;">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light">
  <title>{title}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  </style>
</head>
<body style="margin:0;padding:0;font-family:{_FONT};font-size:16px;line-height:1.68;color:{_BODY};background:{_CREAM};-webkit-font-smoothing:antialiased;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{_CREAM};padding:36px 16px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:560px;background:#FFFFFF;border:1px solid {_BORDER};border-radius:14px;overflow:hidden;font-family:{_FONT};">
        <tr><td style="height:4px;background:{_ORANGE};font-size:0;line-height:0;">&nbsp;</td></tr>
        <tr><td style="padding:30px 34px 0 34px;">
          <div style="font-size:12px;letter-spacing:3.2px;color:{_ORANGE};font-weight:700;text-transform:uppercase;">{product_name}</div>
        </td></tr>
        <tr><td style="padding:10px 34px 0 34px;">
          <h1 style="margin:0;font-family:{_FONT};font-size:24px;line-height:1.3;color:{_INK};font-weight:600;letter-spacing:-0.3px;">{title}</h1>
        </td></tr>
        <tr><td style="padding:16px 34px 30px 34px;color:{_BODY};font-size:15px;line-height:1.68;">
          <p style="margin:0 0 18px;">{body}</p>
          <p style="margin:0;color:{_MUTED};font-size:13px;">Your writing space is waiting. No pressure — just support.</p>
        </td></tr>
        <tr><td style="padding:18px 34px 24px 34px;background:{_CREAM_SOFT};border-top:1px solid {_BORDER};color:{_MUTED};font-size:12px;line-height:1.6;">
          Authora — your book, written with you.
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def reminder_email_plain(title: str, body: str) -> str:
    """Plain text version (always used as fallback)."""
    return f"{title}\n\n{body}\n\n— Your writing space is waiting."
