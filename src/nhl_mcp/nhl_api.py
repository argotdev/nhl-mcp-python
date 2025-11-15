"""
NHL API Client

Interfaces with the official NHL APIs:
- api-web.nhle.com (primary data source)
- api.nhle.com/stats/rest (statistics)
"""

from datetime import datetime
from typing import Any, Optional
import httpx
from pydantic import BaseModel


NHL_API_BASE = "https://api-web.nhle.com/v1"
NHL_STATS_API_BASE = "https://api.nhle.com/stats/rest/en"


class TeamInfo(BaseModel):
    """Team information in a game"""
    id: int
    abbrev: str
    name: str
    score: int


class PeriodDescriptor(BaseModel):
    """Period descriptor"""
    number: int
    period_type: str = ""


class GameScore(BaseModel):
    """Game score information"""
    id: int
    season: int
    game_type: int
    game_date: str
    venue: str
    home_team: TeamInfo
    away_team: TeamInfo
    game_state: str
    period: int
    period_descriptor: Optional[PeriodDescriptor] = None

    class Config:
        populate_by_name = True


class TeamAbbrev(BaseModel):
    """Team abbreviation"""
    default: str


class TeamName(BaseModel):
    """Team name"""
    default: str


class TeamStandings(BaseModel):
    """Team standings information"""
    team_abbrev: TeamAbbrev
    team_name: TeamName
    team_logo: str
    wins: int
    losses: int
    ot_losses: int
    points: int
    games_played: int
    goal_for: int
    goal_against: int
    goal_differential: int
    regulation_wins: int
    win_pctg: float
    conference_abbrev: str
    division_abbrev: str
    place_name: Optional[TeamName] = None

    class Config:
        populate_by_name = True


class PlayerName(BaseModel):
    """Player name"""
    default: str


class PlayerStats(BaseModel):
    """Player statistics"""
    id: int
    first_name: PlayerName
    last_name: PlayerName
    sweater_number: int
    headshot: str
    team_abbrev: str
    team_name: TeamName
    team_logo: str
    position: str
    value: float  # The stat value (points, goals, assists, etc.)

    class Config:
        populate_by_name = True


class GoalieStats(BaseModel):
    """Goalie statistics"""
    id: int
    first_name: PlayerName
    last_name: PlayerName
    sweater_number: int
    headshot: str
    team_abbrev: str
    team_name: TeamName
    team_logo: str
    position: str
    value: float  # The stat value (savePctg, wins, etc.)

    class Config:
        populate_by_name = True


class NHLAPIClient:
    """Client for interacting with NHL APIs"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _fetch_json(self, url: str) -> Any:
        """Fetch JSON data from a URL"""
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_todays_scores(self, date: Optional[str] = None) -> list[dict[str, Any]]:
        """Get today's NHL games with scores and status"""
        date_str = date or datetime.now().date().isoformat()
        data = await self._fetch_json(f"{NHL_API_BASE}/score/{date_str}")
        return data.get("games", [])

    async def get_game_details(self, game_id: int) -> dict[str, Any]:
        """Get detailed game data including play-by-play"""
        return await self._fetch_json(f"{NHL_API_BASE}/gamecenter/{game_id}/play-by-play")

    async def get_game_boxscore(self, game_id: int) -> dict[str, Any]:
        """Get game boxscore with detailed stats"""
        return await self._fetch_json(f"{NHL_API_BASE}/gamecenter/{game_id}/boxscore")

    async def get_standings(self, date: Optional[str] = None) -> dict[str, Any]:
        """Get current standings (optionally by date)"""
        date_str = date or datetime.now().date().isoformat()
        return await self._fetch_json(f"{NHL_API_BASE}/standings/{date_str}")

    async def get_standings_by_season(self, season: str) -> dict[str, Any]:
        """Get standings by season"""
        return await self._fetch_json(f"{NHL_API_BASE}/standings/{season}")

    async def get_team_schedule(
        self, team_abbrev: str, season: Optional[str] = None
    ) -> dict[str, Any]:
        """Get team schedule"""
        season_str = season or self._get_current_season()
        return await self._fetch_json(
            f"{NHL_API_BASE}/club-schedule-season/{team_abbrev}/{season_str}"
        )

    async def get_schedule(self, date: Optional[str] = None) -> dict[str, Any]:
        """Get schedule for a specific week"""
        date_str = date or datetime.now().date().isoformat()
        return await self._fetch_json(f"{NHL_API_BASE}/schedule/{date_str}")

    async def get_player_stats(
        self, player_id: int, season: Optional[str] = None
    ) -> dict[str, Any]:
        """Get player stats for current season"""
        return await self._fetch_json(f"{NHL_API_BASE}/player/{player_id}/landing")

    async def get_top_skaters(
        self,
        category: str = "points",
        limit: int = 20,
        season: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Get top skaters by category"""
        season_str = season or self._get_current_season()

        if not season:
            # Use current stats leaders endpoint
            data = await self._fetch_json(
                f"{NHL_API_BASE}/skater-stats-leaders/current?categories={category}&limit={limit}"
            )
            return data.get(category, [])
        else:
            # Use seasonal stats leaders endpoint
            data = await self._fetch_json(
                f"{NHL_API_BASE}/skater-stats-leaders/{season_str}/2?categories={category}&limit={limit}"
            )
            return data.get(category, [])

    async def get_top_goalies(
        self, limit: int = 20, season: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get top goalies"""
        season_str = season or self._get_current_season()
        category = "savePctg"  # Default to save percentage

        if not season:
            # Use current stats leaders endpoint
            data = await self._fetch_json(
                f"{NHL_API_BASE}/goalie-stats-leaders/current?categories={category}&limit={limit}"
            )
            return data.get(category, [])
        else:
            # Use seasonal stats leaders endpoint
            data = await self._fetch_json(
                f"{NHL_API_BASE}/goalie-stats-leaders/{season_str}/2?categories={category}&limit={limit}"
            )
            return data.get(category, [])

    async def get_playoff_bracket(self, season: Optional[str] = None) -> dict[str, Any]:
        """Get playoff bracket (when available)"""
        year = season or str(datetime.now().year)
        return await self._fetch_json(f"{NHL_API_BASE}/playoff-bracket/{year}")

    async def get_playoff_series(self, season: Optional[str] = None) -> dict[str, Any]:
        """Get playoff series"""
        season_str = season or self._get_current_season()
        return await self._fetch_json(f"{NHL_API_BASE}/playoff-series/{season_str}/playoff")

    async def get_team_stats(
        self, team_abbrev: str, season: Optional[str] = None
    ) -> dict[str, Any]:
        """Get team roster and stats"""
        season_str = season or self._get_current_season()
        return await self._fetch_json(f"{NHL_API_BASE}/club-stats/{team_abbrev}/{season_str}/2")

    async def get_team_roster(
        self, team_abbrev: str, season: Optional[str] = None
    ) -> dict[str, Any]:
        """Get team roster"""
        season_str = season or self._get_current_season()
        return await self._fetch_json(f"{NHL_API_BASE}/roster/{team_abbrev}/{season_str}")

    def _get_current_season(self) -> str:
        """Helper: Get current NHL season ID (e.g., 20242025)"""
        now = datetime.now()
        year = now.year
        month = now.month

        # NHL season typically starts in October
        if month >= 10:
            return f"{year}{year + 1}"
        else:
            return f"{year - 1}{year}"

    def format_season(self, season: str) -> str:
        """Parse season string to readable format"""
        if len(season) == 8:
            start_year = season[:4]
            end_year = season[4:8]
            return f"{start_year}-{end_year}"
        return season
