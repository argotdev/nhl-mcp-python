#!/usr/bin/env python3
"""
NHL MCP Server

Provides tools for querying NHL live data and statistics
"""

import asyncio
import json
import sys
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .nhl_api import NHLAPIClient


# Create NHL API client
client = NHLAPIClient()

# Define available tools
TOOLS: list[Tool] = [
    Tool(
        name="get_live_games",
        description="Get live NHL game scores and status for today or a specific date. Shows current scores, period, game state, and venue information.",
        inputSchema={
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (optional, defaults to today)",
                }
            },
        },
    ),
    Tool(
        name="get_game_details",
        description="Get detailed information about a specific game including play-by-play data, scoring plays, and period summaries.",
        inputSchema={
            "type": "object",
            "properties": {
                "gameId": {
                    "type": "number",
                    "description": "The NHL game ID",
                }
            },
            "required": ["gameId"],
        },
    ),
    Tool(
        name="get_standings",
        description="Get current NHL standings including wins, losses, points, goals for/against, and goal differential. Can filter by division or conference.",
        inputSchema={
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (optional, defaults to current standings)",
                },
                "division": {
                    "type": "string",
                    "description": "Filter by division (Atlantic, Metropolitan, Central, Pacific)",
                },
                "conference": {
                    "type": "string",
                    "description": "Filter by conference (Eastern, Western)",
                },
            },
        },
    ),
    Tool(
        name="get_team_stats",
        description="Get detailed statistics for a specific NHL team including roster, season performance, and player stats.",
        inputSchema={
            "type": "object",
            "properties": {
                "teamAbbrev": {
                    "type": "string",
                    "description": "Team abbreviation (e.g., TOR, NYR, BOS, MTL)",
                },
                "season": {
                    "type": "string",
                    "description": "Season in format YYYYYYYY (e.g., 20242025), defaults to current season",
                },
            },
            "required": ["teamAbbrev"],
        },
    ),
    Tool(
        name="get_player_stats",
        description="Get statistics for top NHL players including goals, assists, points, plus/minus, and other performance metrics.",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category to sort by: points, goals, assists, plusMinus, shots, shootingPctg (defaults to points)",
                },
                "limit": {
                    "type": "number",
                    "description": "Number of players to return (defaults to 20)",
                },
                "season": {
                    "type": "string",
                    "description": "Season in format YYYYYYYY (e.g., 20242025), defaults to current season",
                },
            },
        },
    ),
    Tool(
        name="get_goalie_stats",
        description="Get statistics for NHL goalies including save percentage, GAA, wins, shutouts, and other goalie-specific metrics.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "number",
                    "description": "Number of goalies to return (defaults to 20)",
                },
                "season": {
                    "type": "string",
                    "description": "Season in format YYYYYYYY (e.g., 20242025), defaults to current season",
                },
            },
        },
    ),
    Tool(
        name="get_schedule",
        description="Get NHL schedule for upcoming games. Can get schedule for a specific date or team.",
        inputSchema={
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (optional, defaults to current week)",
                },
                "teamAbbrev": {
                    "type": "string",
                    "description": "Team abbreviation to get specific team schedule (e.g., TOR, NYR)",
                },
            },
        },
    ),
    Tool(
        name="get_playoff_bracket",
        description="Get current playoff bracket with series information, matchups, and results.",
        inputSchema={
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., 2024), defaults to current season",
                }
            },
        },
    ),
    Tool(
        name="compare_teams",
        description="Compare head-to-head statistics between two NHL teams including recent matchups and historical records.",
        inputSchema={
            "type": "object",
            "properties": {
                "team1": {
                    "type": "string",
                    "description": "First team abbreviation (e.g., TOR)",
                },
                "team2": {
                    "type": "string",
                    "description": "Second team abbreviation (e.g., MTL)",
                },
                "season": {
                    "type": "string",
                    "description": "Season in format YYYYYYYY (optional, defaults to current)",
                },
            },
            "required": ["team1", "team2"],
        },
    ),
    Tool(
        name="get_team_streak",
        description="Get current winning or losing streak for an NHL team based on recent game results.",
        inputSchema={
            "type": "object",
            "properties": {
                "teamAbbrev": {
                    "type": "string",
                    "description": "Team abbreviation (e.g., TOR, NYR)",
                }
            },
            "required": ["teamAbbrev"],
        },
    ),
    Tool(
        name="compare_seasons",
        description="Compare team or player statistics across multiple NHL seasons.",
        inputSchema={
            "type": "object",
            "properties": {
                "teamAbbrev": {
                    "type": "string",
                    "description": "Team abbreviation to compare (optional)",
                },
                "seasons": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": 'Array of seasons to compare in format YYYYYYYY (e.g., ["20232024", "20242025"])',
                },
            },
            "required": ["seasons"],
        },
    ),
]


# Helper functions
def format_game_score(game: dict[str, Any]) -> str:
    """Format a game score for display"""
    game_state = game.get("gameState", "")
    period = game.get("period", 0)

    if game_state in ("LIVE", "CRIT"):
        status = f"LIVE - Period {period}"
    elif game_state == "FUT":
        status = "Scheduled"
    elif game_state in ("FINAL", "OFF"):
        status = "Final"
    else:
        status = game_state

    away_team = game.get("awayTeam", {})
    home_team = game.get("homeTeam", {})

    return (
        f"{away_team.get('abbrev', '')} {away_team.get('score', 0)} @ "
        f"{home_team.get('abbrev', '')} {home_team.get('score', 0)} - {status}\n"
        f"Venue: {game.get('venue', '')}\n"
        f"Date: {game.get('gameDate', '')}\n"
        f"Game ID: {game.get('id', '')}"
    )


def format_standings(standings: list[dict[str, Any]]) -> str:
    """Format standings table"""
    result = "Team | GP | W | L | OT | PTS | GF | GA | DIFF | Div\n"
    result += "-" * 70 + "\n"

    for team in standings:
        team_name = team.get("teamAbbrev", {}).get("default", "").ljust(4)
        gp = str(team.get("gamesPlayed", 0)).rjust(3)
        w = str(team.get("wins", 0)).rjust(2)
        l = str(team.get("losses", 0)).rjust(2)
        ot = str(team.get("otLosses", 0)).rjust(2)
        pts = str(team.get("points", 0)).rjust(3)
        gf = str(team.get("goalFor", 0)).rjust(3)
        ga = str(team.get("goalAgainst", 0)).rjust(3)
        diff = str(team.get("goalDifferential", 0)).rjust(4)
        div = team.get("divisionAbbrev", "")

        result += f"{team_name} | {gp} | {w} | {l} | {ot} | {pts} | {gf} | {ga} | {diff} | {div}\n"

    return result


def format_player_stats(players: list[dict[str, Any]], category: str) -> str:
    """Format player statistics table"""
    result = f"Rank | Player | Team | Pos | {category.upper()}\n"
    result += "-" * 60 + "\n"

    for index, player in enumerate(players):
        first_name = player.get("firstName", {}).get("default", "")
        last_name = player.get("lastName", {}).get("default", "")
        name = f"{first_name} {last_name}"
        display_name = name[:25].ljust(25)
        team = player.get("teamAbbrev", "").ljust(4)
        pos = player.get("position", "").ljust(2)
        value = str(player.get("value", 0)).rjust(4)
        rank = str(index + 1).rjust(3)

        result += f"{rank} | {display_name} | {team} | {pos} | {value}\n"

    return result


def format_goalie_stats(goalies: list[dict[str, Any]], category: str) -> str:
    """Format goalie statistics table"""
    result = f"Rank | Goalie | Team | {category.upper()}\n"
    result += "-" * 60 + "\n"

    for index, goalie in enumerate(goalies):
        first_name = goalie.get("firstName", {}).get("default", "")
        last_name = goalie.get("lastName", {}).get("default", "")
        name = f"{first_name} {last_name}"
        display_name = name[:25].ljust(25)
        team = goalie.get("teamAbbrev", "").ljust(4)
        value = goalie.get("value", 0)
        if category == "savePctg":
            value_str = f"{value:.3f}"
        else:
            value_str = str(value)
        rank = str(index + 1).rjust(3)

        result += f"{rank} | {display_name} | {team} | {value_str}\n"

    return result


async def analyze_streak(team_abbrev: str) -> str:
    """Analyze a team's current winning or losing streak"""
    try:
        schedule = await client.get_team_schedule(team_abbrev)

        games = schedule.get("games", [])
        if not games:
            return f"No games found for {team_abbrev}"

        # Get completed games sorted by date
        completed_games = [
            g for g in games if g.get("gameState") in ("OFF", "FINAL")
        ]
        completed_games.sort(
            key=lambda x: x.get("gameDate", ""), reverse=True
        )

        if not completed_games:
            return f"No completed games found for {team_abbrev} this season"

        streak_count = 0
        streak_type = ""
        recent_results: list[str] = []

        for game in completed_games:
            is_home = game.get("homeTeam", {}).get("abbrev") == team_abbrev
            team_score = (
                game.get("homeTeam", {}).get("score", 0)
                if is_home
                else game.get("awayTeam", {}).get("score", 0)
            )
            opp_score = (
                game.get("awayTeam", {}).get("score", 0)
                if is_home
                else game.get("homeTeam", {}).get("score", 0)
            )
            opp_team = (
                game.get("awayTeam", {}).get("abbrev", "")
                if is_home
                else game.get("homeTeam", {}).get("abbrev", "")
            )

            won = team_score > opp_score
            result = "W" if won else "L"

            recent_results.append(f"{result} {team_score}-{opp_score} vs {opp_team}")

            if streak_count == 0:
                streak_type = result
                streak_count = 1
            elif result == streak_type:
                streak_count += 1
            else:
                break

            if len(recent_results) >= 10:
                break

        streak_text = (
            f"{streak_count} game winning streak"
            if streak_type == "W"
            else f"{streak_count} game losing streak"
        )

        return (
            f"{team_abbrev} Current Streak: {streak_text}\n\n"
            f"Last 10 games:\n" + "\n".join(recent_results)
        )
    except Exception as e:
        return f"Error analyzing streak: {str(e)}"


async def compare_teams_head_to_head(
    team1: str, team2: str, season: Optional[str] = None
) -> str:
    """Compare two teams head-to-head"""
    try:
        schedule1 = await client.get_team_schedule(team1, season)

        games = schedule1.get("games", [])
        if not games:
            return f"No schedule data found for {team1}"

        # Find games between these two teams
        matchups = [
            game
            for game in games
            if (
                game.get("homeTeam", {}).get("abbrev") == team1
                and game.get("awayTeam", {}).get("abbrev") == team2
            )
            or (
                game.get("homeTeam", {}).get("abbrev") == team2
                and game.get("awayTeam", {}).get("abbrev") == team1
            )
        ]

        if not matchups:
            return f"No matchups found between {team1} and {team2} this season"

        team1_wins = 0
        team2_wins = 0
        results: list[str] = []

        for game in matchups:
            is_team1_home = game.get("homeTeam", {}).get("abbrev") == team1
            team1_score = (
                game.get("homeTeam", {}).get("score", 0)
                if is_team1_home
                else game.get("awayTeam", {}).get("score", 0)
            )
            team2_score = (
                game.get("awayTeam", {}).get("score", 0)
                if is_team1_home
                else game.get("homeTeam", {}).get("score", 0)
            )
            game_state = game.get("gameState", "")

            if game_state in ("OFF", "FINAL"):
                if team1_score > team2_score:
                    team1_wins += 1
                    results.append(
                        f"{game.get('gameDate', '')}: {team1} {team1_score}, "
                        f"{team2} {team2_score} - {team1} WIN"
                    )
                else:
                    team2_wins += 1
                    results.append(
                        f"{game.get('gameDate', '')}: {team1} {team1_score}, "
                        f"{team2} {team2_score} - {team2} WIN"
                    )
            elif game_state == "FUT":
                results.append(f"{game.get('gameDate', '')}: Upcoming game")
            else:
                results.append(
                    f"{game.get('gameDate', '')}: {team1} {team1_score}, "
                    f"{team2} {team2_score} - IN PROGRESS"
                )

        return (
            f"Head-to-Head: {team1} vs {team2}\n\n"
            f"Season Series: {team1} {team1_wins}-{team2_wins} {team2}\n\n"
            f"Games:\n" + "\n".join(results)
        )
    except Exception as e:
        return f"Error comparing teams: {str(e)}"


async def compare_seasons(
    seasons: list[str], team_abbrev: Optional[str] = None
) -> str:
    """Compare statistics across multiple seasons"""
    try:
        if not team_abbrev:
            # Compare league-wide stats
            results: list[str] = []

            for season in seasons:
                standings_data = await client.get_standings_by_season(season)
                teams = standings_data.get("standings", [])

                total_goals = sum(t.get("goalFor", 0) for t in teams)
                total_games = sum(t.get("gamesPlayed", 0) for t in teams)

                avg_goals = total_goals / total_games if total_games > 0 else 0

                results.append(
                    f"Season {client.format_season(season)}:\n"
                    f"  Total teams: {len(teams)}\n"
                    f"  Total goals: {total_goals}\n"
                    f"  Avg goals/game: {avg_goals:.2f}"
                )

            return "Season Comparison:\n\n" + "\n\n".join(results)
        else:
            # Compare specific team across seasons
            results: list[str] = []

            for season in seasons:
                standings_data = await client.get_standings_by_season(season)
                teams = standings_data.get("standings", [])
                team = next(
                    (
                        t
                        for t in teams
                        if t.get("teamAbbrev", {}).get("default") == team_abbrev
                    ),
                    None,
                )

                if team:
                    results.append(
                        f"{client.format_season(season)} - {team_abbrev}:\n"
                        f"  Record: {team.get('wins', 0)}-{team.get('losses', 0)}-{team.get('otLosses', 0)}\n"
                        f"  Points: {team.get('points', 0)}\n"
                        f"  Goals For: {team.get('goalFor', 0)}\n"
                        f"  Goals Against: {team.get('goalAgainst', 0)}\n"
                        f"  Goal Diff: {team.get('goalDifferential', 0)}"
                    )
                else:
                    results.append(
                        f"{client.format_season(season)} - {team_abbrev}: No data found"
                    )

            return f"Season Comparison for {team_abbrev}:\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Error comparing seasons: {str(e)}"


# Create MCP server
app = Server("nhl-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    try:
        if name == "get_live_games":
            games = await client.get_todays_scores(arguments.get("date"))
            if not games:
                return [TextContent(type="text", text="No games scheduled for this date")]
            formatted = "\n\n".join(format_game_score(game) for game in games)
            return [TextContent(type="text", text=formatted)]

        elif name == "get_game_details":
            details = await client.get_game_details(int(arguments["gameId"]))
            return [TextContent(type="text", text=json.dumps(details, indent=2))]

        elif name == "get_standings":
            standings_data = await client.get_standings(arguments.get("date"))
            filtered = standings_data.get("standings", [])

            if "division" in arguments:
                division = arguments["division"].lower()
                filtered = [
                    t
                    for t in filtered
                    if t.get("divisionAbbrev", "").lower() == division
                ]

            if "conference" in arguments:
                conference = arguments["conference"].lower()
                filtered = [
                    t
                    for t in filtered
                    if t.get("conferenceAbbrev", "").lower() == conference
                ]

            formatted = format_standings(filtered)
            return [TextContent(type="text", text=formatted)]

        elif name == "get_team_stats":
            stats = await client.get_team_stats(
                arguments["teamAbbrev"], arguments.get("season")
            )
            return [TextContent(type="text", text=json.dumps(stats, indent=2))]

        elif name == "get_player_stats":
            category = arguments.get("category", "points")
            players = await client.get_top_skaters(
                category, arguments.get("limit", 20), arguments.get("season")
            )
            formatted = format_player_stats(players, category)
            return [TextContent(type="text", text=formatted)]

        elif name == "get_goalie_stats":
            goalies = await client.get_top_goalies(
                arguments.get("limit", 20), arguments.get("season")
            )
            formatted = format_goalie_stats(goalies, "savePctg")
            return [TextContent(type="text", text=formatted)]

        elif name == "get_schedule":
            if "teamAbbrev" in arguments:
                schedule = await client.get_team_schedule(
                    arguments["teamAbbrev"], arguments.get("season")
                )
            else:
                schedule = await client.get_schedule(arguments.get("date"))
            return [TextContent(type="text", text=json.dumps(schedule, indent=2))]

        elif name == "get_playoff_bracket":
            bracket = await client.get_playoff_bracket(arguments.get("season"))
            return [TextContent(type="text", text=json.dumps(bracket, indent=2))]

        elif name == "compare_teams":
            comparison = await compare_teams_head_to_head(
                arguments["team1"], arguments["team2"], arguments.get("season")
            )
            return [TextContent(type="text", text=comparison)]

        elif name == "get_team_streak":
            streak = await analyze_streak(arguments["teamAbbrev"])
            return [TextContent(type="text", text=streak)]

        elif name == "compare_seasons":
            comparison = await compare_seasons(
                arguments["seasons"], arguments.get("teamAbbrev")
            )
            return [TextContent(type="text", text=comparison)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Main entry point for the server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
