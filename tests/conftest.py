"""Shared test helpers."""
from pathlib import Path

import pytest
from mcp.types import CallToolRequestParams
from signal_mcp.server import call_tool as _call_tool, get_client, TOOLS  # re-export for tests


@pytest.fixture(autouse=True)
def widen_send_roots(monkeypatch, tmp_path_factory):
    """Tests across this suite use throwaway paths -- literal "/tmp/..." or
    pytest's own tmp_path -- as stand-ins for attachment/avatar/sticker-pack
    paths; none of them are actually read from disk by the code under test
    (the RPC call itself is always mocked), so widen the SIGNAL_MCP_SEND_ROOTS
    allowlist (see config.validate_send_path) to cover both for the whole
    suite rather than rewriting every test's fixture path."""
    import signal_mcp.config as _config_mod
    monkeypatch.setattr(_config_mod, "SEND_ROOTS", [
        *_config_mod.SEND_ROOTS, Path("/tmp"), tmp_path_factory.getbasetemp(),
    ])


async def call_tool(name: str, arguments: dict):
    """Thin shim so existing tests keep their (name, args) call signature."""
    return (await _call_tool(None, CallToolRequestParams(name=name, arguments=arguments))).content
