import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from typing import Dict, Any


TEST_TOPIC = "Product Feedback Topic"
TEST_USERNAME = "alice_tester"
TEST_SECRET = "super_secret_password"


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Returns valid auth headers."""
    return {"X-Username": TEST_USERNAME, "X-Secret": TEST_SECRET}


@pytest.fixture
def valid_payload() -> Dict[str, Any]:
    """Default valid payload for creating an inbox."""
    return {
        "topic": TEST_TOPIC,
        "username": TEST_USERNAME,
        "secret": TEST_SECRET,
        "allow_anonymous": True,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    }


@pytest.fixture
def create_inbox(client: AsyncClient, api_prefix: str, valid_payload: Dict[str, Any]):
    """
    Factory fixture returning an async function that creates an inbox.
    Allows per-test payload overrides.
    """

    async def _factory(custom_payload: Dict[str, Any] = None):
        payload = custom_payload or valid_payload
        url = f"{api_prefix}/inboxes/"
        resp = await client.post(url, json=payload)

        assert resp.status_code == 201, f"Setup failed: {resp.text}"

        data = resp.json()
        return data, data["id"]

    return _factory


@pytest.mark.asyncio
async def test_create_inbox_success(
    client: AsyncClient, api_prefix: str, valid_payload
):
    """Creates an inbox directly (without helper) to verify the endpoint."""
    url = f"{api_prefix}/inboxes/"
    resp = await client.post(url, json=valid_payload)

    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert "signature" in data


@pytest.mark.asyncio
async def test_public_access_returns_topic(
    client: AsyncClient, api_prefix: str, create_inbox
):
    # Arrange: use factory with a custom topic
    custom_payload = _get_valid_payload_copy_with(topic="Public Topic Check")
    _, inbox_id = await create_inbox(custom_payload)

    # Act
    resp = await client.get(f"{api_prefix}/inboxes/{inbox_id}")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert data["topic"] == "Public Topic Check"
    assert data["allow_anonymous"] is True
    assert "messages" not in data


@pytest.mark.asyncio
async def test_messages_unauthorized_access(
    client: AsyncClient, api_prefix: str, create_inbox
):
    # Arrange
    _, inbox_id = await create_inbox()

    # Act: read WITHOUT headers
    resp = await client.get(f"{api_prefix}/inboxes/{inbox_id}/messages")

    # Assert
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_messages_empty_for_new_inbox_with_auth(
    client: AsyncClient, api_prefix: str, create_inbox, auth_headers
):
    # Arrange
    _, inbox_id = await create_inbox()

    # Act: fetch WITH headers
    resp = await client.get(
        f"{api_prefix}/inboxes/{inbox_id}/messages", headers=auth_headers
    )

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert data["messages"] == []


@pytest.mark.asyncio
async def test_post_message_and_fetch_with_auth(
    client: AsyncClient, api_prefix: str, create_inbox, auth_headers
):
    # Arrange: create inbox
    _, inbox_id = await create_inbox()

    # Act 1: post message (anonymous)
    reply_url = f"{api_prefix}/inboxes/{inbox_id}/messages"
    reply_payload = {"body": "This is a test message!"}

    reply_resp = await client.post(reply_url, json=reply_payload)
    assert reply_resp.status_code == 201

    # Act 2: fetch messages as owner
    read_resp = await client.get(
        f"{api_prefix}/inboxes/{inbox_id}/messages", headers=auth_headers
    )

    # Assert
    assert read_resp.status_code == 200
    messages = read_resp.json()["messages"]

    assert len(messages) == 1
    msg = messages[0]
    assert msg["body"] == "This is a test message!"
    assert "id" in msg
    assert "created_at" in msg


@pytest.mark.asyncio
async def test_create_inbox_invalid_payload(client: AsyncClient, api_prefix: str):
    """Validation: missing fields should return 422."""
    url = f"{api_prefix}/inboxes/"
    invalid_payload = {"topic": "Just a topic"}

    resp = await client.post(url, json=invalid_payload)

    assert resp.status_code == 422
    errors = resp.json()["detail"]

    # Extract field names from validation errors
    error_fields = {str(err["loc"][-1]) for err in errors}

    assert {"username", "secret", "expires_at"}.issubset(error_fields)


def _get_valid_payload_copy_with(**kwargs):
    """
    Utility to quickly create modified payloads
    without overriding the global fixture.
    """
    payload = {
        "topic": TEST_TOPIC,
        "username": TEST_USERNAME,
        "secret": TEST_SECRET,
        "allow_anonymous": True,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    }
    payload.update(kwargs)
    return payload
