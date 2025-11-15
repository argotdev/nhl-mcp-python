"""Entry point for running the NHL MCP server"""

import asyncio
import sys

from .server import main

if __name__ == "__main__":
    asyncio.run(main())
