# NHL MCP Server (Python)

A Model Context Protocol (MCP) server that provides access to NHL live data and statistics through natural language queries. This is an idiomatic Python implementation of the NHL MCP server.

## Features

- **Live Game Data**: Get real-time scores, game status, and schedules
- **Team Statistics**: Access comprehensive team performance data
- **Player Statistics**: Query top players by various categories (points, goals, assists, etc.)
- **Goalie Statistics**: Specialized goalie metrics including save percentage and GAA
- **Standings**: Current NHL standings with filtering by division or conference
- **Head-to-Head Comparisons**: Compare teams and analyze matchup history
- **Streak Analysis**: Track team winning/losing streaks
- **Season Comparisons**: Compare statistics across multiple NHL seasons
- **Playoff Data**: Access playoff brackets and series information

## Installation

### From Source

1. Clone this repository
2. Install dependencies:

```bash
cd nhl-mcp-python
pip install -e .
```

### Using pip (once published)

```bash
pip install nhl-mcp-server
```

## Usage

### Running the Server

The server communicates via stdio and is designed to be used with MCP clients:

```bash
python -m nhl_mcp.server
```

Or if installed via pip:

```bash
nhl-mcp-server
```

### Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "nhl": {
      "command": "python",
      "args": ["-m", "nhl_mcp.server"]
    }
  }
}
```

Or if using a virtual environment:

```json
{
  "mcpServers": {
    "nhl": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "nhl_mcp.server"]
    }
  }
}
```

## Available Tools

### `get_live_games`
Get live NHL game scores and status for today or a specific date.

**Parameters:**
- `date` (optional): Date in YYYY-MM-DD format

**Example:**
```
Get today's NHL scores
Show me games on 2024-03-15
```

### `get_game_details`
Get detailed information about a specific game including play-by-play data.

**Parameters:**
- `gameId` (required): The NHL game ID

**Example:**
```
Get details for game 2024020123
```

### `get_standings`
Get current NHL standings with optional filtering.

**Parameters:**
- `date` (optional): Date in YYYY-MM-DD format
- `division` (optional): Atlantic, Metropolitan, Central, or Pacific
- `conference` (optional): Eastern or Western

**Example:**
```
Show me the Atlantic division standings
Get Eastern conference standings
```

### `get_team_stats`
Get detailed statistics for a specific NHL team.

**Parameters:**
- `teamAbbrev` (required): Team abbreviation (e.g., TOR, NYR, BOS)
- `season` (optional): Season in format YYYYYYYY (e.g., 20242025)

**Example:**
```
Get Toronto Maple Leafs stats
Show me Boston Bruins statistics
```

### `get_player_stats`
Get statistics for top NHL players.

**Parameters:**
- `category` (optional): points, goals, assists, plusMinus, shots, shootingPctg
- `limit` (optional): Number of players to return (default: 20)
- `season` (optional): Season in format YYYYYYYY

**Example:**
```
Show me top goal scorers
Get top 10 players by points
```

### `get_goalie_stats`
Get statistics for NHL goalies.

**Parameters:**
- `limit` (optional): Number of goalies to return (default: 20)
- `season` (optional): Season in format YYYYYYYY

**Example:**
```
Show me top goalies
Get top 15 goalies by save percentage
```

### `get_schedule`
Get NHL schedule for upcoming games.

**Parameters:**
- `date` (optional): Date in YYYY-MM-DD format
- `teamAbbrev` (optional): Team abbreviation for specific team schedule

**Example:**
```
Show me the Maple Leafs schedule
Get NHL schedule for next week
```

### `get_playoff_bracket`
Get current playoff bracket information.

**Parameters:**
- `season` (optional): Season year (e.g., 2024)

**Example:**
```
Show me the current playoff bracket
Get 2024 playoff bracket
```

### `compare_teams`
Compare head-to-head statistics between two teams.

**Parameters:**
- `team1` (required): First team abbreviation
- `team2` (required): Second team abbreviation
- `season` (optional): Season in format YYYYYYYY

**Example:**
```
Compare Toronto and Montreal
Show me Bruins vs Rangers head to head
```

### `get_team_streak`
Get current winning or losing streak for a team.

**Parameters:**
- `teamAbbrev` (required): Team abbreviation

**Example:**
```
What's the Maple Leafs current streak?
Show me Boston's win/loss streak
```

### `compare_seasons`
Compare statistics across multiple NHL seasons.

**Parameters:**
- `seasons` (required): Array of seasons to compare
- `teamAbbrev` (optional): Team abbreviation for team-specific comparison

**Example:**
```
Compare the 2023-24 and 2024-25 seasons for Toronto
Compare league stats between 20232024 and 20242025
```

## Team Abbreviations

Common NHL team abbreviations:
- **Atlantic**: TOR (Toronto), BOS (Boston), MTL (Montreal), TBL (Tampa Bay), FLA (Florida), OTT (Ottawa), DET (Detroit), BUF (Buffalo)
- **Metropolitan**: NYR (Rangers), NYI (Islanders), CAR (Carolina), NJD (New Jersey), PHI (Philadelphia), PIT (Pittsburgh), WSH (Washington), CBJ (Columbus)
- **Central**: COL (Colorado), DAL (Dallas), MIN (Minnesota), WPG (Winnipeg), NSH (Nashville), STL (St. Louis), ARI (Arizona), CHI (Chicago)
- **Pacific**: VGK (Vegas), EDM (Edmonton), LAK (Los Angeles), SEA (Seattle), CGY (Calgary), VAN (Vancouver), SJS (San Jose), ANA (Anaheim)

## API Data Sources

This server interfaces with the official NHL APIs:
- `api-web.nhle.com` - Primary data source for games, standings, and schedules
- `api.nhle.com/stats/rest` - Statistics and player data

## Development

### Requirements

- Python 3.10 or higher
- Dependencies listed in `requirements.txt`

### Project Structure

```
nhl-mcp-python/
├── src/
│   └── nhl_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py      # Main MCP server implementation
│       └── nhl_api.py     # NHL API client with type models
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Code Style

This implementation follows Python best practices:
- Type hints throughout using Python 3.10+ syntax
- Pydantic models for data validation
- Async/await for all I/O operations
- Snake_case naming conventions
- Comprehensive docstrings

### Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests (if you add them)
pytest
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
