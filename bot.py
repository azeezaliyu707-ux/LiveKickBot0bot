import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from config import Config
from handlers import BotHandlers, AI_CHAT

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Initialize handlers
    handlers = BotHandlers()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("live", handlers.show_live_scores))
    application.add_handler(CommandHandler("fixtures", handlers.show_fixtures))
    application.add_handler(CommandHandler("standings", handlers.show_standings_menu))
    application.add_handler(CommandHandler("insights", handlers.match_insights))
    
    # Add conversation handler for AI chat
    ai_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("ai", handlers.ai_assistant),
            CallbackQueryHandler(handlers.ai_assistant, pattern='^ai_assistant$')
        ],
        states={
            AI_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_ai_chat)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.start_command, pattern='^start$')
        ]
    )
    application.add_handler(ai_conv_handler)
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(handlers.button_callback))
    
    # Start the bot
    logger.info("LiveKickBot0bot is starting...")
    logger.info(f"OpenAI API Key present: {bool(Config.OPENAI_API_KEY)}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
