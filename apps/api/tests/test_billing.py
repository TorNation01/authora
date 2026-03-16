"""Billing API tests - entitlements, plans, admin grants, promo codes."""

import pytest


@pytest.mark.asyncio
async def test_list_plans_public(anon_client):
    """Plans list is public."""
    resp = await anon_client.get("/api/v1/billing/plans")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    slugs = [p["slug"] for p in data]
    assert "free" in slugs


@pytest.mark.asyncio
async def test_billing_status_requires_auth(anon_client):
    """Billing status requires auth."""
    resp = await anon_client.get("/api/v1/billing/status")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_billing_status_returns_plan(auth_client):
    """Billing status returns plan and usage."""
    resp = await auth_client.get("/api/v1/billing/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "plan" in data
    assert "usage" in data
    assert data["plan"]["slug"] in ("free", "starter", "pro", "studio", "founder_lifetime")


@pytest.mark.asyncio
async def test_admin_billing_health_requires_admin(auth_client, admin_client):
    """Billing health requires admin."""
    resp = await auth_client.get("/api/v1/billing/admin/health")
    assert resp.status_code == 403

    resp = await admin_client.get("/api/v1/billing/admin/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "stripe_configured" in data
    assert "plans_count" in data


@pytest.mark.asyncio
async def test_admin_grants_requires_admin(auth_client, admin_client, test_user):
    """Create grant requires admin."""
    resp = await auth_client.post(
        "/api/v1/billing/admin/grants",
        json={"user_id": str(test_user.id), "plan_slug": "pro", "reason": "support_resolution"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_promo_codes_requires_admin(auth_client):
    """List promo codes requires admin."""
    resp = await auth_client.get("/api/v1/billing/admin/promo-codes")
    assert resp.status_code == 403
