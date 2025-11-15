"""NHL MCP Server - Model Context Protocol server for NHL data"""

__version__ = "1.0.0"

from .nhl_api import NHLAPIClient
from .server import app

__all__ = ["NHLAPIClient", "app"]
