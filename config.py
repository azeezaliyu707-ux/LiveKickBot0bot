import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Default leagues to track
    DEFAULT_LEAGUES = [
        {'name': 'Premier League', 'country': 'England'},
        {'name': 'La Liga', 'country': 'Spain'},
        {'name': 'Serie A', 'country': 'Italy'},
        {'name': 'Bundesliga', 'country': 'Germany'},
        {'name': 'Ligue 1', 'country': 'France'},
        {'name': 'UEFA Champions League', 'country': 'Europe'}
    ]
    
    # Top teams for quick access
    TOP_TEAMS = [
        'Manchester City', 'Real Madrid', 'Bayern Munich', 'PSG', 
        'Liverpool', 'Barcelona', 'AC Milan', 'Arsenal',
        'Chelsea', 'Manchester United', 'Juventus', 'Inter Milan'
    ]
