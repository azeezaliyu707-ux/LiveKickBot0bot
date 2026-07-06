import aiohttp
import asyncio
from datetime import datetime, timedelta
from config import Config
import logging

logger = logging.getLogger(__name__)

class FootballAPI:
    def __init__(self):
        self.api_key = Config.FOOTBALL_API_KEY
        self.base_url = Config.FOOTBALL_API_URL
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': Config.FOOTBALL_API_HOST
        }
    
    async def get_live_scores(self):
        """Get all live matches"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/fixtures"
                params = {
                    'live': 'all',
                    'timezone': 'UTC'
                }
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', [])
                    else:
                        logger.error(f"API Error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching live scores: {e}")
            return []
    
    async def get_fixtures(self, date=None):
        """Get fixtures for a specific date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/fixtures"
                params = {
                    'date': date,
                    'timezone': 'UTC'
                }
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', [])
                    else:
                        return []
        except Exception as e:
            logger.error(f"Error fetching fixtures: {e}")
            return []
    
    async def get_league_standings(self, league_id, season=2024):
        """Get league standings"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/standings"
                params = {
                    'league': league_id,
                    'season': season
                }
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', [])
                    else:
                        return []
        except Exception as e:
            logger.error(f"Error fetching standings: {e}")
            return []
    
    async def get_team_lineup(self, fixture_id):
        """Get lineup for a specific match"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/fixtures/lineups"
                params = {
                    'fixture': fixture_id
                }
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', [])
                    else:
                        return []
        except Exception as e:
            logger.error(f"Error fetching lineup: {e}")
            return []

    async def get_match_events(self, fixture_id):
        """Get match events (goals, cards, substitutions)"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/fixtures/events"
                params = {
                    'fixture': fixture_id
                }
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', [])
                    else:
                        return []
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []

    def format_live_score(self, match):
        """Format match data for display"""
        try:
            home = match['teams']['home']
            away = match['teams']['away']
            goals = match['goals']
            status = match['fixture']['status']['short']
            
            # Get events if available
            events = match.get('events', [])
            goal_events = [e for e in events if e['type'] == 'Goal']
            card_events = [e for e in events if e['type'] in ['Yellow Card', 'Red Card']]
            
            score_text = f"⚽ {home['name']} {goals['home']} - {goals['away']} {away['name']}\n"
            score_text += f"🕐 Status: {status}\n"
            
            # Add recent goals
            if goal_events:
                score_text += "\n⚽ Goals:\n"
                for goal in goal_events[-3:]:  # Show last 3 goals
                    scorer = goal.get('player', {}).get('name', 'Unknown')
                    assist = goal.get('assist', {}).get('name', '')
                    minute = goal.get('time', {}).get('elapsed', 0)
                    score_text += f"  • {minute}' - {scorer}"
                    if assist:
                        score_text += f" (assist: {assist})"
                    score_text += "\n"
            
            # Add cards
            if card_events:
                score_text += "\n🟨🟥 Cards:\n"
                for card in card_events[-3:]:
                    player = card.get('player', {}).get('name', 'Unknown')
                    card_type = card.get('type', 'Card')
                    minute = card.get('time', {}).get('elapsed', 0)
                    emoji = '🟨' if card_type == 'Yellow Card' else '🟥'
                    score_text += f"  • {emoji} {minute}' - {player}\n"
            
            return score_text
        except Exception as e:
            logger.error(f"Error formatting score: {e}")
            return "Error formatting match data"
