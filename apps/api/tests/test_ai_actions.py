"""AI actions API tests."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_actions_public(client: AsyncClient):
    """List AI actions is public."""
    res = await client.get("/api/v1/ai/actions")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_run_action_requires_auth(client: AsyncClient):
    """Run action requires auth."""
    res = await client.post(
        "/api/v1/ai/actions/run",
        json={
            "action_id": "rewrite_sentence",
            "book_id": str(uuid.uuid4()),
            "selection": "test",
        },
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_run_action_validation(auth_client: AsyncClient):
    """Invalid action_id rejected."""
    res = await auth_client.post(
        "/api/v1/ai/actions/run",
        json={
            "action_id": "invalid_action",
            "book_id": str(uuid.uuid4()),
        },
    )
    assert res.status_code in (400, 404, 422)
