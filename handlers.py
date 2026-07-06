import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from football_data import FootballData
from openai import AsyncOpenAI
from config import Config
import logging

logger = logging.getLogger(__name__)

# Conversation states
AI_CHAT = 1

class BotHandlers:
    def __init__(self):
        self.football_data = FootballData()
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [InlineKeyboardButton("📊 Live Scores", callback_data='live_scores')],
            [InlineKeyboardButton("📅 Today's Fixtures", callback_data='fixtures')],
            [InlineKeyboardButton("🏆 League Standings", callback_data='standings')],
            [InlineKeyboardButton("🤖 AI Assistant", callback_data='ai_assistant')],
            [InlineKeyboardButton("⚽ Match Insights", callback_data='match_insights')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "⚽ **Welcome to LiveKickBot0bot!** ⚽\n\n"
            "Your AI-powered football companion. I provide:\n"
            "• 📊 Live scores from matches worldwide\n"
            "• ⚽ Goals, cards, and match events\n"
            "• 📅 Fixtures for today's matches\n"
            "• 🏆 League standings for top competitions\n"
            "• 🤖 AI-powered match insights and analysis\n\n"
            "**Powered by OpenAI** - Get intelligent football updates!\n\n"
            "Choose an option below to get started:"
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
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
        elif data == 'ai_assistant':
            await self.ai_assistant(update, context)
        elif data == 'match_insights':
            await self.match_insights(update, context)
        elif data == 'help':
            await self.help_command(update, context)
        elif data.startswith('standings_'):
            league_name = data.split('_')[1]
            await self.show_league_standings(update, context, league_name)
        elif data.startswith('insight_'):
            match_id = data.split('_')[1]
            await self.show_match_insight(update, context, match_id)
    
    async def show_live_scores(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show live scores"""
        await update.callback_query.edit_message_text("⏳ Fetching live scores...")
        
        matches = await self.football_data.get_live_scores()
        
        if not matches:
            await update.callback_query.edit_message_text(
                "📭 No live matches at the moment. Check back later!"
            )
            return
        
        response_text = "⚽ **LIVE MATCHES** ⚽\n\n"
        
        for match in matches:
            response_text += self.football_data.format_live_score(match)
            response_text += "\n" + "─"*30 + "\n\n"
        
        # Add AI insight for first match if available
        if matches and self.openai_client:
            try:
                insight = await self.football_data.get_match_insight(matches[0])
                response_text += f"🤖 **AI Match Insight:**\n{insight}\n\n"
            except:
                pass
        
        # Add refresh button
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data='live_scores')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            response_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def show_fixtures(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show today's fixtures"""
        await update.callback_query.edit_message_text("⏳ Fetching today's fixtures...")
        
        fixtures = await self.football_data.get_fixtures()
        
        if not fixtures:
            await update.callback_query.edit_message_text(
                "📭 No fixtures scheduled for today."
            )
            return
        
        response_text = "📅 **TODAY'S FIXTURES** 📅\n\n"
        
        for fixture in fixtures[:12]:
            response_text += f"⚽ {fixture['home']} vs {fixture['away']}\n"
            response_text += f"🏆 {fixture['league']}\n"
            response_text += f"🕐 {fixture['time']} - {fixture['status']}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data='fixtures')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            response_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def show_standings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show league selection menu for standings"""
        keyboard = []
        for league in Config.DEFAULT_LEAGUES:
            keyboard.append([InlineKeyboardButton(
                f"🏆 {league['name']}",
                callback_data=f'standings_{league["name"]}'
            )])
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='start')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            "🏆 **Select a league to view standings:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_league_standings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, league_name):
        """Show league standings"""
        await update.callback_query.edit_message_text(f"⏳ Fetching {league_name} standings...")
        
        standings = await self.football_data.get_league_standings(league_name)
        
        if not standings:
            await update.callback_query.edit_message_text(
                f"❌ Could not fetch standings for {league_name}."
            )
            return
        
        response_text = f"🏆 **{league_name} Standings** 🏆\n\n"
        
        for team in standings:
            response_text += f"{team['position']}. {team['team']} - {team['points']} pts\n"
            response_text += f"   P: {team['played']} W: {team['won']} D: {team['drawn']} L: {team['lost']}\n"
            response_text += f"   GF: {team['goals_for']} GA: {team['goals_against']}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Leagues", callback_data='standings')],
            [InlineKeyboardButton("🔄 Refresh", callback_data=f'standings_{league_name}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            response_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def ai_assistant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AI-powered football assistant"""
        if not self.openai_client:
            await update.callback_query.edit_message_text(
                "🤖 AI assistant is currently unavailable. Please check your OpenAI API key."
            )
            return
        
        await update.callback_query.edit_message_text(
            "🤖 **AI Football Assistant** 🤖\n\n"
            "Ask me anything about football! I can help with:\n"
            "• 📊 Match predictions and analysis\n"
            "• ⚽ Player statistics and information\n"
            "• 🏆 League standings and history\n"
            "• 📋 Football rules and regulations\n"
            "• 📈 Team performance analysis\n\n"
            "**Type your question below** (or type /cancel to exit):"
        )
        
        return AI_CHAT
    
    async def handle_ai_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle AI chat messages"""
        if not self.openai_client:
            await update.message.reply_text("🤖 AI assistant is currently unavailable.")
            return ConversationHandler.END
        
        question = update.message.text
        
        if question.lower() == '/cancel':
            await update.message.reply_text("❌ AI chat cancelled.")
            return ConversationHandler.END
        
        # Send typing indicator
        await update.message.chat.send_action(action="typing")
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a knowledgeable football expert assistant. 
                    Provide accurate, helpful information about football matches, rules, teams, players, 
                    competitions, history, and statistics. Be enthusiastic and engaging."""},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Split long messages
            if len(answer) > 4096:
                for i in range(0, len(answer), 4096):
                    await update.message.reply_text(f"🤖 {answer[i:i+4096]}")
            else:
                await update.message.reply_text(f"🤖 {answer}")
            
            # Ask if they want to continue
            keyboard = [
                [InlineKeyboardButton("💬 Ask Another Question", callback_data='ai_assistant')],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data='start')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Would you like to ask another question?",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"AI Error: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't process your question. Please try again later.\n"
                "Type /cancel to exit AI chat."
            )
        
        return AI_CHAT
    
    async def match_insights(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show match insights"""
        matches = await self.football_data.get_live_scores()
        
        if not matches:
            await update.callback_query.edit_message_text(
                "📭 No live matches to analyze at the moment."
            )
            return
        
        keyboard = []
        for match in matches[:5]:
            match_id = match.get('id', f"{match['home']}_{match['away']}")
            label = f"⚽ {match['home']} vs {match['away']} ({match['home_score']}-{match['away_score']})"
            keyboard.append([InlineKeyboardButton(label, callback_data=f'insight_{match_id}')])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='start')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            "⚽ **Select a match for AI insights:**\n\n"
            "Get detailed analysis and predictions from our AI assistant.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_match_insight(self, update: Update, context: ContextTypes.DEFAULT_TYPE, match_id):
        """Show detailed insight for a specific match"""
        await update.callback_query.edit_message_text("🤖 Generating AI insights...")
        
        matches = await self.football_data.get_live_scores()
        match = next((m for m in matches if m.get('id') == match_id), None)
        
        if not match:
            # Try to find by home/away
            for m in matches:
                if f"{m['home']}_{m['away']}" == match_id:
                    match = m
                    break
        
        if not match:
            await update.callback_query.edit_message_text(
                "❌ Match not found. Please try again."
            )
            return
        
        # Get AI insight
        insight = await self.football_data.get_match_insight(match)
        
        response_text = f"⚽ **Match Analysis** ⚽\n\n"
        response_text += f"**{match['home']} {match['home_score']} - {match['away_score']} {match['away']}**\n"
        response_text += f"🏆 {match['league']} | 🕐 {match['minute']}'\n\n"
        response_text += f"🤖 **AI Analysis:**\n{insight}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Insight", callback_data=f'insight_{match_id}')],
            [InlineKeyboardButton("📊 Live Score", callback_data='live_scores')],
            [InlineKeyboardButton("🔙 Back", callback_data='match_insights')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            response_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
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
            "/ai - Chat with AI assistant\n"
            "/insights - Get match insights\n\n"
            "**Features:**\n"
            "• Real-time live scores (AI-generated)\n"
            "• Goals, cards, and match events\n"
            "• League standings for top competitions\n"
            "• AI-powered match insights\n"
            "• Intelligent football chat assistant\n\n"
            "**Powered by OpenAI** 🤖\n\n"
            "Stay connected with your favorite teams!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                help_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel conversation"""
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
