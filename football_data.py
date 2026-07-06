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
        self.fixtures = []
        self.teams_by_league = {
            'Premier League': ['Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Manchester United', 'Tottenham', 'Newcastle', 'Aston Villa'],
            'La Liga': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Valencia', 'Real Sociedad'],
            'Serie A': ['AC Milan', 'Inter Milan', 'Juventus', 'Roma', 'Napoli', 'Lazio'],
            'Bundesliga': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen', 'Eintracht Frankfurt'],
            'Ligue 1': ['PSG', 'Marseille', 'Lyon', 'Monaco', 'Lille'],
            'UEFA Champions League': ['Real Madrid', 'Manchester City', 'Bayern Munich', 'PSG', 'Liverpool', 'AC Milan']
        }
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize sample match data structure"""
        # Generate some sample fixtures for today
        self._generate_sample_fixtures(datetime.now().strftime('%Y-%m-%d'))
        
        # Generate some live matches
        sample_matches = [
            {
                'id': 'match_1',
                'league': 'Premier League',
                'home': 'Manchester City',
                'away': 'Liverpool',
                'home_score': 2,
                'away_score': 1,
                'minute': 67,
                'status': 'Live',
                'events': [
                    {'type': 'Goal', 'minute': 23, 'player': 'Haaland', 'team': 'Manchester City'},
                    {'type': 'Goal', 'minute': 45, 'player': 'Salah', 'team': 'Liverpool'},
                    {'type': 'Goal', 'minute': 78, 'player': 'Foden', 'team': 'Manchester City'}
                ]
            },
            {
                'id': 'match_2',
                'league': 'La Liga',
                'home': 'Real Madrid',
                'away': 'Barcelona',
                'home_score': 1,
                'away_score': 1,
                'minute': 55,
                'status': 'Live',
                'events': [
                    {'type': 'Goal', 'minute': 12, 'player': 'Vinicius Jr', 'team': 'Real Madrid'},
                    {'type': 'Goal', 'minute': 38, 'player': 'Lewandowski', 'team': 'Barcelona'},
                    {'type': 'Yellow Card', 'minute': 42, 'player': 'Araujo', 'team': 'Barcelona'}
                ]
            },
            {
                'id': 'match_3',
                'league': 'Bundesliga',
                'home': 'Bayern Munich',
                'away': 'Borussia Dortmund',
                'home_score': 3,
                'away_score': 0,
                'minute': 72,
                'status': 'Live',
                'events': [
                    {'type': 'Goal', 'minute': 15, 'player': 'Kane', 'team': 'Bayern Munich'},
                    {'type': 'Goal', 'minute': 34, 'player': 'Musiala', 'team': 'Bayern Munich'},
                    {'type': 'Goal', 'minute': 56, 'player': 'Sane', 'team': 'Bayern Munich'}
                ]
            }
        ]
        
        for match in sample_matches:
            self.live_matches[match['id']] = match
    
    async def get_live_scores(self):
        """Get live matches"""
        # Update scores randomly to simulate live action
        for match in self.live_matches.values():
            if match['status'] == 'Live':
                # Randomly update score
                if random.random() < 0.05:  # 5% chance of goal
                    if random.random() < 0.5:
                        match['home_score'] += 1
                    else:
                        match['away_score'] += 1
                # Update minute
                match['minute'] = min(match['minute'] + random.randint(1, 3), 90)
                if match['minute'] >= 90:
                    match['status'] = 'Finished'
        
        return list(self.live_matches.values())
    
    async def get_fixtures(self, date=None):
        """Get fixtures for a specific date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # If no fixtures or different date, generate new ones
        if not self.fixtures or self.fixtures[0].get('date') != date:
            self._generate_sample_fixtures(date)
        
        return self.fixtures
    
    def _generate_sample_fixtures(self, date):
        """Generate sample fixtures"""
        fixtures = []
        leagues = list(self.teams_by_league.keys())
        
        for _ in range(10):  # Generate 10 fixtures
            league = random.choice(leagues)
            teams = self.teams_by_league[league]
            
            if len(teams) >= 2:
                home, away = random.sample(teams, 2)
                hour = random.randint(12, 22)
                minute = random.choice(['00', '15', '30', '45'])
                
                fixtures.append({
                    'league': league,
                    'home': home,
                    'away': away,
                    'time': f"{hour:02d}:{minute}",
                    'date': date,
                    'status': 'Scheduled'
                })
        
        self.fixtures = fixtures
    
    async def get_league_standings(self, league_name):
        """Get standings for a specific league"""
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
