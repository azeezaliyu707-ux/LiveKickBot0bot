import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Football API (we'll use API-Football from rapidapi)
    # You can get free API key from: https://rapidapi.com/api-sports/api/api-football/
    FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')
    FOOTBALL_API_HOST = 'api-football-v1.p.rapidapi.com'
    FOOTBALL_API_URL = 'https://api-football-v1.p.rapidapi.com/v3'
    
    # Default leagues to track
    DEFAULT_LEAGUES = [
        {'id': 39, 'name': 'Premier League'},
        {'id': 140, 'name': 'La Liga'},
        {'id': 135, 'name': 'Serie A'},
        {'id': 78, 'name': 'Bundesliga'},
        {'id': 61, 'name': 'Ligue 1'},
        {'id': 2, 'name': 'Champions League'}
    ]
