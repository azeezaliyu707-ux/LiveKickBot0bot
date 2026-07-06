import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from football_api import FootballAPI
from openai import AsyncOpenAI
from config import Config
import logging

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_OPTION, SELECTING_LEAGUE, SELECTING_MATCH = range(3)

class BotHandlers:
    def __init__(self):
        self.football_api = FootballAPI()
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [InlineKeyboardButton("📊 Live Scores", callback_data='live_scores')],
            [InlineKeyboardButton("📅 Today's Fixtures", callback_data='fixtures')],
            [InlineKeyboardButton("🏆 League Standings", callback_data='standings')],
            [InlineKeyboardButton("⚽ Match Lineup", callback_data='lineup')],
            [InlineKeyboardButton("🤖 AI Assistant", callback_data='ai_assistant')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "⚽ Welcome to LiveKickBot0bot!\n\n"
            "Your real-time football companion. I provide:\n"
            "• Live scores from matches worldwide\n"
            "• Goals, cards, and match events\n"
            "• Team lineups and formations\n"
            "• Fixtures and league standings\n"
            "• AI-powered football insights\n\n"
            "Choose an option below to get started:"
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == 'live_scores':
            await self.show_live_scores(update, context)
        elif data == 'fixtures':
            await self.show_fixtures(update, context)
        elif data == 'standings':
            await self.show_standings_menu(update, context)
        elif data == 'lineup':
            await self.show_lineup_menu(update, context)
        elif data == 'ai_assistant':
            await self.ai_assistant(update, context)
        elif data == 'help':
            await self.help_command(update, context)
        elif data.startswith('standings_'):
            league_id = int(data.split('_')[1])
            await self.show_league_standings(update, context, league_id)
        elif data.startswith('lineup_'):
            fixture_id = int(data.split('_')[1])
            await self.show_match_lineup(update, context, fixture_id)
    
    async def show_live_scores(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show live scores"""
        await update.callback_query.edit_message_text("⏳ Fetching live scores...")
        
        matches = await self.football_api.get_live_scores()
        
        if not matches:
            await update.callback_query.edit_message_text(
                "📭 No live matches at the moment. Check back later!"
            )
            return
        
        response_text = "⚽ **LIVE MATCHES** ⚽\n\n"
        
        for match in matches[:10]:  # Limit to 10 matches
            response_text += self.football_api.format_live_score(match)
            response_text += "\n" + "─"*30 + "\n\n"
        
        if len(matches) > 10:
            response_text += f"\n... and {len(matches)-10} more matches"
        
        # Use OpenAI to add some insights if available
        if self.openai_client:
            try:
                ai_insight = await self.get_ai_insight(matches[:3])
                response_text += f"\n🤖 **AI Insight:**\n{ai_insight}"
            except:
                pass
        
        await update.callback_query.edit_message_text(
            response_text,
            parse_mode='Markdown'
        )
    
    async def show_fixtures(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show today's fixtures"""
        await update.callback_query.edit_message_text("⏳ Fetching today's fixtures...")
        
        fixtures = await self.football_api.get_fixtures()
        
        if not fixtures:
            await update.callback_query.edit_message_text(
                "📭 No fixtures scheduled for today."
            )
            return
        
        response_text = "📅 **TODAY'S FIXTURES** 📅\n\n"
        
        for fixture in fixtures[:10]:
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            time = fixture['fixture']['date'].split('T')[1][:5]
            league = fixture['league']['name']
            
            response_text += f"⚽ {home} vs {away}\n"
            response_text += f"🕐 {time} - {league}\n\n"
        
        await update.callback_query.edit_message_text(
            response_text,
            parse_mode='Markdown'
        )
    
    async def show_standings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show league selection menu for standings"""
        keyboard = []
        for league in Config.DEFAULT_LEAGUES:
            keyboard.append([InlineKeyboardButton(
                league['name'],
                callback_data=f'standings_{league["id"]}'
            )])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='start')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            "🏆 **Select a league to view standings:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_league_standings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, league_id):
        """Show league standings"""
        await update.callback_query.edit_message_text("⏳ Fetching standings...")
        
        standings = await self.football_api.get_league_standings(league_id)
        
        if not standings or not standings[0].get('league', {}).get('standings'):
            await update.callback_query.edit_message_text(
                "❌ Could not fetch standings for this league."
            )
            return
        
        league_standings = standings[0]['league']['standings'][0]
        
        league_name = standings[0]['league']['name']
        response_text = f"🏆 **{league_name} Standings** 🏆\n\n"
        
        for idx, team in enumerate(league_standings[:10], 1):
            response_text += f"{idx}. {team['team']['name']} - {team['points']} pts\n"
            response_text += f"   P: {team['all']['played']} W: {team['all']['win']} D: {team['all']['draw']} L: {team['all']['lose']}\n"
            response_text += f"   GF: {team['all']['goals']['for']} GA: {team['all']['goals']['against']}\n\n"
        
        await update.callback_query.edit_message_text(
            response_text,
            parse_mode='Markdown'
        )
    
    async def show_lineup_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recent matches to select lineup"""
        await update.callback_query.edit_message_text(
            "⏳ Fetching recent matches... This feature requires a fixture ID.\n"
            "Please use the command: /lineup [fixture_id]"
        )
    
    async def show_match_lineup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, fixture_id):
        """Show match lineup"""
        await update.callback_query.edit_message_text("⏳ Fetching lineup...")
        
        lineup_data = await self.football_api.get_team_lineup(fixture_id)
        
        if not lineup_data:
            await update.callback_query.edit_message_text(
                "❌ Could not fetch lineup for this match."
            )
            return
        
        response_text = "⚽ **Match Lineup** ⚽\n\n"
        
        for team_lineup in lineup_data:
            team_name = team_lineup['team']['name']
            response_text += f"**{team_name}**\n"
            
            players = team_lineup.get('lineup', [])[:11]
            for player in players:
                position = player.get('pos', '')
                name = player.get('player', {}).get('name', 'Unknown')
                response_text += f"  • {position}: {name}\n"
            
            response_text += "\n"
        
        await update.callback_query.edit_message_text(
            response_text,
            parse_mode='Markdown'
        )
    
    async def ai_assistant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AI-powered football assistant"""
        if not self.openai_client:
            await update.callback_query.edit_message_text(
                "🤖 AI assistant is currently unavailable."
            )
            return
        
        await update.callback_query.edit_message_text(
            "🤖 **AI Football Assistant**\n\n"
            "Ask me anything about football! Send a question like:\n"
            "• Who is the top scorer in Premier League?\n"
            "• Tell me about the latest match updates\n"
            "• Explain the offside rule\n"
            "• Who will win the Champions League?\n\n"
            "Type your question:"
        )
    
    async def handle_ai_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle AI questions"""
        if not self.openai_client:
            await update.message.reply_text("🤖 AI assistant is currently unavailable.")
            return
        
        question = update.message.text
        
        await update.message.reply_text("🤔 Thinking...")
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a football expert assistant. Provide accurate, helpful information about football matches, rules, teams, players, and competitions."},
                    {"role": "user", "content": question}
                ],
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            await update.message.reply_text(f"🤖 {answer}")
            
        except Exception as e:
            logger.error(f"AI Error: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't process your question. Please try again."
            )
    
    async def get_ai_insight(self, matches):
        """Get AI insights about matches"""
        if not self.openai_client:
            return ""
        
        match_text = ""
        for match in matches[:3]:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            score = f"{match['goals']['home']}-{match['goals']['away']}"
            match_text += f"{home} vs {away} ({score})\n"
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Provide a brief 1-2 sentence insight about these football matches."},
                    {"role": "user", "content": match_text}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content
        except:
            return ""
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = (
            "⚽ **LiveKickBot0bot Help** ⚽\n\n"
            "**Commands:**\n"
            "/start - Show main menu\n"
            "/help - Show this help\n"
            "/live - Show live scores\n"
            "/fixtures - Show today's fixtures\n"
            "/standings - Show league standings\n"
            "/lineup [fixture_id] - Show match lineup\n"
            "/ai [question] - Ask AI assistant\n\n"
            "**Features:**\n"
            "• Real-time live scores\n"
            "• Goals, cards, and match events\n"
            "• Team lineups\n"
            "• League standings\n"
            "• AI-powered insights\n\n"
            "Stay connected with your favorite teams!"
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                help_text,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(help_text, parse_mode='Markdown')
