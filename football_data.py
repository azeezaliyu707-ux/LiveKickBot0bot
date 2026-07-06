import json
import random
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from config import Config
import logging

logger = logging.getLogger(__name__)

class FootballData:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
        self.live_matches = {}
        self.match_history = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize sample match data structure"""
        # Sample teams by league
        self.teams_by_league = {
            'Premier League': ['Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Manchester United', 'Tottenham', 'Newcastle', 'Aston Villa'],
            'La Liga': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Valencia', 'Real Sociedad'],
            'Serie A': ['AC Milan', 'Inter Milan', 'Juventus', 'Roma', 'Napoli', 'Lazio'],
            'Bundesliga': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen', 'Eintracht Frankfurt'],
            'Ligue 1': ['PSG', 'Marseille', 'Lyon', 'Monaco', 'Lille'],
            'UEFA Champions League': ['Real Madrid', 'Manchester City', 'Bayern Munich', 'PSG', 'Liverpool', 'AC Milan']
        }
        
        # Current date for fixtures
        today = datetime.now()
        
        # Generate some sample fixtures for today
        self.fixtures = []
        for league, teams in self.teams_by_league.items():
            for i in range(0, len(teams)-1, 2):
                if len(teams) > i+1:
                    match_time = today.replace(hour=random.randint(12, 22), minute=random.choice([0, 15, 30, 45]))
                    self.fixtures.append({
                        'league': league,
                        'home': teams[i],
                        'away': teams[i+1],
                        'time': match_time.strftime('%H:%M'),
                        'date': today.strftime('%Y-%m-%d'),
                        'status': 'Scheduled'
                    })
        
        # Generate some live matches
        for i in range(3):
            league = list(self.teams_by_league.keys())[i % len(self.teams_by_league)]
            teams = self.teams_by_league[league]
            home = teams[i % len(teams)]
            away = teams[(i+2) % len(teams)]
            
            # Random score
            home_goals = random.randint(0, 3)
            away_goals = random.randint(0, 3)
            minute = random.randint(10, 89)
            
            # Generate some events
            events = []
            for _ in range(random.randint(1, 3)):
                event_type = random.choice(['Goal', 'Yellow Card', 'Red Card'])
                event_minute = random.randint(5, 89)
                if event_type == 'Goal':
                    scorer = random.choice([home, away])
                    events.append({
                        'type': 'Goal',
                        'minute': event_minute,
                        'player': f'{scorer} #{random.randint(7, 20)}',
                        'team': scorer
                    })
                else:
                    player = random.choice([home, away])
                    events.append({
                        'type': event_type,
                        'minute': event_minute,
                        'player': f'{player} #{random.randint(2, 30)}',
                        'team': player
                    })
            
            self.live_matches[f"match_{i+1}"] = {
                'id': f"match_{i+1}",
                'league': league,
                'home': home,
                'away': away,
                'home_score': home_goals,
                'away_score': away_goals,
                'minute': minute,
                'status': 'Live',
                'events': sorted(events, key=lambda x: x['minute'])
            }
    
    async def get_live_scores(self):
        """Get live matches with AI-generated updates"""
        if not self.live_matches:
            return await self._generate_live_matches_ai()
        return list(self.live_matches.values())
    
    async def _generate_live_matches_ai(self):
        """Generate live matches using OpenAI"""
        if not self.openai_client:
            return self._generate_sample_live_matches()
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a football data generator. Generate realistic live football matches 
                    with scores, events, and statistics. Format as JSON with this structure:
                    {
                        "matches": [
                            {
                                "league": "Premier League",
                                "home": "Manchester City",
                                "away": "Liverpool",
                                "home_score": 2,
                                "away_score": 1,
                                "minute": 67,
                                "events": [
                                    {"type": "Goal", "minute": 23, "player": "Haaland", "team": "Manchester City"},
                                    {"type": "Yellow Card", "minute": 45, "player": "Van Dijk", "team": "Liverpool"}
                                ]
                            }
                        ]
                    }
                    Only include 3-5 matches from different leagues. Make scores and events realistic."""},
                    {"role": "user", "content": "Generate current live football matches with realistic scores and events."}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            data = json.loads(response.choices[0].message.content)
            matches = data.get('matches', [])
            
            # Store in live_matches
            for idx, match in enumerate(matches):
                self.live_matches[f"match_{idx+1}"] = match
            
            return matches
            
        except Exception as e:
            logger.error(f"Error generating AI matches: {e}")
            return self._generate_sample_live_matches()
    
    def _generate_sample_live_matches(self):
        """Generate sample live matches as fallback"""
        matches = []
        sample_matches = [
            {
                'league': 'Premier League',
                'home': 'Manchester City',
                'away': 'Liverpool',
                'home_score': 2,
                'away_score': 1,
                'minute': 67,
                'events': [
                    {'type': 'Goal', 'minute': 23, 'player': 'Haaland', 'team': 'Manchester City'},
                    {'type': 'Goal', 'minute': 45, 'player': 'Salah', 'team': 'Liverpool'},
                    {'type': 'Goal', 'minute': 78, 'player': 'Foden', 'team': 'Manchester City'}
                ]
            },
            {
                'league': 'La Liga',
                'home': 'Real Madrid',
                'away': 'Barcelona',
                'home_score': 1,
                'away_score': 1,
                'minute': 55,
                'events': [
                    {'type': 'Goal', 'minute': 12, 'player': 'Vinicius Jr', 'team': 'Real Madrid'},
                    {'type': 'Goal', 'minute': 38, 'player': 'Lewandowski', 'team': 'Barcelona'},
                    {'type': 'Yellow Card', 'minute': 42, 'player': 'Araujo', 'team': 'Barcelona'}
                ]
            },
            {
                'league': 'Bundesliga',
                'home': 'Bayern Munich',
                'away': 'Borussia Dortmund',
                'home_score': 3,
                'away_score': 0,
                'minute': 72,
                'events': [
                    {'type': 'Goal', 'minute': 15, 'player': 'Kane', 'team': 'Bayern Munich'},
                    {'type': 'Goal', 'minute': 34, 'player': 'Musiala', 'team': 'Bayern Munich'},
                    {'type': 'Goal', 'minute': 56, 'player': 'Sane', 'team': 'Bayern Munich'}
                ]
            }
        ]
        
        for idx, match in enumerate(sample_matches):
            self.live_matches[f"match_{idx+1}"] = match
            matches.append(match)
        
        return matches
    
    async def get_fixtures(self, date=None):
        """Get fixtures for a specific date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # If no fixtures or different date, generate new ones
        if not self.fixtures or self.fixtures[0]['date'] != date:
            await self._generate_fixtures_ai(date)
        
        return self.fixtures
    
    async def _generate_fixtures_ai(self, date):
        """Generate fixtures using OpenAI"""
        if not self.openai_client:
            self._generate_sample_fixtures(date)
            return
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""Generate realistic football fixtures for {date}. 
                    Include matches from Premier League, La Liga, Serie A, Bundesliga, Ligue 1, and Champions League.
                    Format as JSON with this structure:
                    {{
                        "fixtures": [
                            {{
                                "league": "Premier League",
                                "home": "Manchester City",
                                "away": "Arsenal",
                                "time": "15:00"
                            }}
                        ]
                    }}
                    Include 8-12 matches. Use realistic team names and times between 12:00 and 22:00."""}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            data = json.loads(response.choices[0].message.content)
            fixtures = data.get('fixtures', [])
            
            # Add date to fixtures
            for fixture in fixtures:
                fixture['date'] = date
                fixture['status'] = 'Scheduled'
            
            self.fixtures = fixtures
            
        except Exception as e:
            logger.error(f"Error generating AI fixtures: {e}")
            self._generate_sample_fixtures(date)
    
    def _generate_sample_fixtures(self, date):
        """Generate sample fixtures as fallback"""
        fixtures = []
        for league, teams in self.teams_by_league.items():
            for i in range(0, len(teams)-1, 2):
                if len(teams) > i+1:
                    fixtures.append({
                        'league': league,
                        'home': teams[i],
                        'away': teams[i+1],
                        'time': f"{random.randint(12, 22):02d}:{random.choice(['00', '15', '30', '45'])}",
                        'date': date,
                        'status': 'Scheduled'
                    })
        self.fixtures = fixtures[:15]  # Limit to 15 fixtures
    
    async def get_league_standings(self, league_name):
        """Get standings for a specific league using AI"""
        if not self.openai_client:
            return self._generate_sample_standings(league_name)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""Generate realistic league standings for {league_name}.
                    Format as JSON with this structure:
                    {{
                        "standings": [
                            {{
                                "position": 1,
                                "team": "Manchester City",
                                "played": 20,
                                "won": 15,
                                "drawn": 3,
                                "lost": 2,
                                "goals_for": 45,
                                "goals_against": 15,
                                "points": 48
                            }}
                        ]
                    }}
                    Include top 10 teams. Make stats realistic."""}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            data = json.loads(response.choices[0].message.content)
            return data.get('standings', [])
            
        except Exception as e:
            logger.error(f"Error generating AI standings: {e}")
            return self._generate_sample_standings(league_name)
    
    def _generate_sample_standings(self, league_name):
        """Generate sample standings as fallback"""
        teams = self.teams_by_league.get(league_name, ['Team A', 'Team B', 'Team C', 'Team D'])
        
        standings = []
        for idx, team in enumerate(teams[:10], 1):
            played = random.randint(18, 22)
            won = random.randint(8, 16)
            drawn = random.randint(2, 6)
            lost = played - won - drawn
            
            standings.append({
                'position': idx,
                'team': team,
                'played': played,
                'won': won,
                'drawn': drawn,
                'lost': lost,
                'goals_for': random.randint(20, 50),
                'goals_against': random.randint(10, 30),
                'points': (won * 3) + drawn
            })
        
        return sorted(standings, key=lambda x: x['points'], reverse=True)
    
    async def get_match_insight(self, match_data):
        """Get AI insight about a match"""
        if not self.openai_client:
            return "Match is in progress. Stay tuned for updates!"
        
        try:
            match_text = f"{match_data['home']} vs {match_data['away']} ({match_data['home_score']}-{match_data['away_score']})"
            events_text = "\n".join([f"{e['minute']}' - {e['type']}: {e['player']} ({e['team']})" for e in match_data.get('events', [])])
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a football analyst. Provide brief, insightful analysis of the match."},
                    {"role": "user", "content": f"Analyze this match: {match_text}\nEvents: {events_text}"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting match insight: {e}")
            return "Exciting match in progress! Check the score above."
    
    def format_live_score(self, match):
        """Format match data for display"""
        try:
            score_text = f"⚽ **{match['home']} {match['home_score']} - {match['away_score']} {match['away']}**\n"
            score_text += f"🏆 League: {match['league']}\n"
            score_text += f"🕐 {match['minute']}' - {match['status']}\n\n"
            
            # Add events
            if match.get('events'):
                score_text += "📊 **Match Events:**\n"
                for event in match['events']:
                    if event['type'] == 'Goal':
                        emoji = '⚽'
                    elif event['type'] == 'Yellow Card':
                        emoji = '🟨'
                    elif event['type'] == 'Red Card':
                        emoji = '🟥'
                    else:
                        emoji = '📌'
                    
                    score_text += f"  • {emoji} {event['minute']}' - {event['player']} ({event['team']})\n"
            
            return score_text
        except Exception as e:
            logger.error(f"Error formatting score: {e}")
            return "Error formatting match data"
