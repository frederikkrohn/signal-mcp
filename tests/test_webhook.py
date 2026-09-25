"""Tests for signal_mcp.webhook — post_webhook and post_webhook_batch."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

from signal_mcp.models import Message
from signal_mcp.webhook import post_webhook, post_webhook_batch

WEBHOOK_URL = "http://localhost:9999/hook"


def make_message(id_: str = "1", sender: str = "+19999999999") -> Message:
    return Message(id=id_, sender=sender, body="hi", timestamp=datetime(2024, 1, 1, 12, 0, 0))


@respx.mock
@pytest.mark.asyncio
async def test_post_webhook_success_first_attempt():
    respx.post(WEBHOOK_URL).mock(return_value=httpx.Response(200))
    result = await post_webhook(WEBHOOK_URL, make_message())
    assert result is True
    assert respx.calls.call_count == 1


@respx.mock
@pytest.mark.asyncio
async def test_post_webhook_success_after_one_retry():
    respx.post(WEBHOOK_URL).mock(
        side_effect=[httpx.Response(500), httpx.Response(200)]
    )
    with patch("signal_mcp.webhook.asyncio.sleep", new=AsyncMock()) as mock_sleep:
        result = await post_webhook(WEBHOOK_URL, make_message())
    assert result is True
    assert respx.calls.call_count == 2
    mock_sleep.assert_called_once_with(0.5)


@respx.mock
@pytest.mark.asyncio
async def test_post_webhook_all_attempts_fail(caplog):
    respx.post(WEBHOOK_URL).mock(return_value=httpx.Response(500))
    with patch("signal_mcp.webhook.asyncio.sleep", new=AsyncMock()):
        with caplog.at_level("WARNING"):
            result = await post_webhook(WEBHOOK_URL, make_message())
    assert result is False
    assert respx.calls.call_count == 3  # initial + 2 retries
    assert "Webhook POST" in caplog.text


@respx.mock
@pytest.mark.asyncio
async def test_post_webhook_exponential_backoff():
    respx.post(WEBHOOK_URL).mock(return_value=httpx.Response(500))
    with patch("signal_mcp.webhook.asyncio.sleep", new=AsyncMock()) as mock_sleep:
        await post_webhook(WEBHOOK_URL, make_message())
    assert [c.args[0] for c in mock_sleep.call_args_list] == [0.5, 1.0]


@respx.mock
@pytest.mark.asyncio
async def test_post_webhook_batch_empty():
    result = await post_webhook_batch(WEBHOOK_URL, [])
    assert result == 0


@respx.mock
@pytest.mark.asyncio
async def test_post_webhook_batch_mixed_results():
    calls = {"n": 0}

    def responder(request):
        calls["n"] += 1
        # message from sender "ok" succeeds, other sender always fails
        if b"+10000000001" in request.content:
            return httpx.Response(200)
        return httpx.Response(500)

    respx.post(WEBHOOK_URL).mock(side_effect=responder)
    messages = [make_message(id_="1", sender="+10000000001"), make_message(id_="2", sender="+10000000002")]
    with patch("signal_mcp.webhook.asyncio.sleep", new=AsyncMock()):
        result = await post_webhook_batch(WEBHOOK_URL, messages)
    assert result == 1
