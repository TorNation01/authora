"""Cloudflare Turnstile verification.

Turnstile replaces the invite gate as the thing standing between a bot and a
new account once signup is open. The token is single-use, must be checked
server-side, and the check must fail closed: a Cloudflare outage that silently
returned "ok" would reopen signup to scripted abuse.
"""

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)


class TurnstileUnavailable(RuntimeError):
    """Raised when Cloudflare could not be reached — not a rejected token."""


async def verify_turnstile_token(
    token: str,
    secret: str,
    remote_ip: str | None = None,
    verify_url: str = "https://challenges.cloudflare.com/turnstile/v0/siteverify",
    timeout: float = 10.0,
) -> bool:
    """Return True only when Cloudflare itself confirms the token."""
    payload = {"secret": secret, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            res = await client.post(verify_url, data=payload)
            res.raise_for_status()
            body = res.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.error("Turnstile verification unavailable: %s", exc)
        raise TurnstileUnavailable(str(exc)) from exc

    if not body.get("success"):
        logger.warning(
            "Turnstile rejected signup token: %s",
            body.get("error-codes") or body.get("messages") or "no detail",
        )
        return False
    return True


def site_key_for_browser(secret: str, site_key: str) -> str:
    """The site key ships to the browser only when the check is armed."""
    return site_key if (secret and site_key) else ""
