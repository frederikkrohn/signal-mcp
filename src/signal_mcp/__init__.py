"""signal-mcp: Complete Signal MCP server and CLI via signal-cli."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("signal-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
