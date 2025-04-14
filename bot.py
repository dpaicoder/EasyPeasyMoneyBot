import os
import logging
import random
import string
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from database import (
    init_db,
    get_session,
    get_user_by_telegram_id,
    create_user,
    get_task_by_id,
    create_task_completion,
    create_transaction,
)
from models import User, Task, TaskCompletion, Transaction

# Load environment variables
load_dotenv()

# Configure logging to stdout
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout  # Ensure logs go to stdout
)

# Get logger
logger = logging.getLogger(__name__)

# Log startup information
logger.info("Starting bot initialization...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Environment variables loaded: {bool(os.getenv('BOT_TOKEN'))}")

# Generate a random referral code
def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user = update.effective_user
    referral_code = context.args[0] if context.args else None
    
    async with get_session() as session:
        # Check if user already exists
        existing_user = await get_user_by_telegram_id(session, user.id)
        
        if not existing_user:
            # Create new user
            new_referral_code = generate_referral_code()
            new_user = await create_user(
                session,
                user.id,
                user.username,
                user.first_name,
                user.last_name,
                new_referral_code
            )
            
            # If user came through referral
            if referral_code:
                referrer = await session.execute(
                    User.__table__.select().where(User.referral_code == referral_code)
                )
                referrer = referrer.scalar_one_or_none()
                if referrer:
                    new_user.referred_by = referrer.id
                    await session.commit()
                    
                    # Create referral bonus transaction
                    await create_transaction(
                        session,
                        referrer.id,
                        float(os.getenv('REFERRAL_BONUS', '10.0')),
                        'referral_bonus'
                    )
        
        # Send welcome message
        keyboard = [
            [
                InlineKeyboardButton("🎯 Available Tasks", callback_data='tasks'),
                InlineKeyboardButton("💰 My Balance", callback_data='balance')
            ],
            [
                InlineKeyboardButton("👥 My Referrals", callback_data='referrals'),
                InlineKeyboardButton("📊 Statistics", callback_data='stats')
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            f"👋 Welcome to the Refer & Earn Bot!\n\n"
            f"🎯 Complete tasks to earn rewards\n"
            f"👥 Invite friends and earn bonuses\n"
            f"💰 Withdraw your earnings\n\n"
            f"Your referral code: `{new_referral_code}`\n"
            f"Share this code with friends to earn bonuses!"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    help_text = (
        "🤖 *Refer & Earn Bot Help*\n\n"
        "🎯 *Tasks*\n"
        "- View available tasks\n"
        "- Complete tasks to earn rewards\n"
        "- Submit proof of completion\n\n"
        "👥 *Referrals*\n"
        "- Share your referral code\n"
        "- Earn bonuses when friends join\n"
        "- Track your referral earnings\n\n"
        "💰 *Balance*\n"
        "- Check your current balance\n"
        "- View transaction history\n"
        "- Request withdrawals\n\n"
        "📊 *Statistics*\n"
        "- View your earnings\n"
        "- Track completed tasks\n"
        "- Monitor referral progress"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Callback query handlers
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'tasks':
        await show_tasks(update, context)
    elif query.data == 'balance':
        await show_balance(update, context)
    elif query.data == 'referrals':
        await show_referrals(update, context)
    elif query.data == 'stats':
        await show_stats(update, context)
    elif query.data == 'help':
        await help_command(update, context)

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available tasks"""
    async with get_session() as session:
        # Get active tasks
        result = await session.execute(
            Task.__table__.select().where(Task.is_active == True)
        )
        tasks = result.scalars().all()
        
        if not tasks:
            await update.callback_query.message.reply_text(
                "No tasks available at the moment. Check back later!"
            )
            return
        
        keyboard = []
        for task in tasks:
            keyboard.append([
                InlineKeyboardButton(
                    f"{task.title} - ${task.reward}",
                    callback_data=f'task_{task.id}'
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            "🎯 *Available Tasks*\n\n"
            "Select a task to view details and start earning!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's balance and transaction history"""
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_user_by_telegram_id(session, user.id)
        
        if not db_user:
            await update.callback_query.message.reply_text(
                "You need to start the bot first! Use /start"
            )
            return
        
        # Get recent transactions
        result = await session.execute(
            Transaction.__table__.select()
            .where(Transaction.user_id == db_user.id)
            .order_by(Transaction.created_at.desc())
            .limit(5)
        )
        transactions = result.scalars().all()
        
        balance_text = (
            f"💰 *Your Balance*\n\n"
            f"Current Balance: ${db_user.balance:.2f}\n\n"
            f"📊 *Recent Transactions*\n"
        )
        
        for transaction in transactions:
            balance_text += (
                f"- {transaction.type}: ${transaction.amount:.2f} "
                f"({transaction.status})\n"
            )
        
        keyboard = [
            [
                InlineKeyboardButton("💳 Withdraw", callback_data='withdraw'),
                InlineKeyboardButton("📋 All Transactions", callback_data='transactions')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            balance_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's referrals"""
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_user_by_telegram_id(session, user.id)
        
        if not db_user:
            await update.callback_query.message.reply_text(
                "You need to start the bot first! Use /start"
            )
            return
        
        # Get referrals
        result = await session.execute(
            User.__table__.select().where(User.referred_by == db_user.id)
        )
        referrals = result.scalars().all()
        
        referrals_text = (
            f"👥 *Your Referrals*\n\n"
            f"Your Referral Code: `{db_user.referral_code}`\n\n"
            f"Total Referrals: {len(referrals)}\n\n"
            f"*Recent Referrals:*\n"
        )
        
        for referral in referrals[:5]:  # Show last 5 referrals
            referrals_text += f"- {referral.username or referral.first_name}\n"
        
        keyboard = [
            [
                InlineKeyboardButton("📤 Share Code", callback_data='share_code'),
                InlineKeyboardButton("📊 Referral Stats", callback_data='referral_stats')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            referrals_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's statistics"""
    user = update.effective_user
    async with get_session() as session:
        db_user = await get_user_by_telegram_id(session, user.id)
        
        if not db_user:
            await update.callback_query.message.reply_text(
                "You need to start the bot first! Use /start"
            )
            return
        
        # Get completed tasks
        result = await session.execute(
            TaskCompletion.__table__.select()
            .where(TaskCompletion.user_id == db_user.id)
            .where(TaskCompletion.status == 'approved')
        )
        completed_tasks = result.scalars().all()
        
        # Get total earnings
        result = await session.execute(
            Transaction.__table__.select()
            .where(Transaction.user_id == db_user.id)
            .where(Transaction.status == 'completed')
        )
        transactions = result.scalars().all()
        
        total_earnings = sum(t.amount for t in transactions)
        
        stats_text = (
            f"📊 *Your Statistics*\n\n"
            f"💰 Total Earnings: ${total_earnings:.2f}\n"
            f"🎯 Completed Tasks: {len(completed_tasks)}\n"
            f"👥 Total Referrals: {len(db_user.referrals)}\n"
            f"📅 Member Since: {db_user.created_at.strftime('%Y-%m-%d')}\n\n"
            f"*Recent Activity*\n"
        )
        
        # Add recent activity
        recent_tasks = completed_tasks[-5:] if completed_tasks else []
        for task in recent_tasks:
            stats_text += f"- Completed task: {task.task.title}\n"
        
        keyboard = [
            [
                InlineKeyboardButton("📈 Detailed Stats", callback_data='detailed_stats'),
                InlineKeyboardButton("🏆 Leaderboard", callback_data='leaderboard')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, an error occurred while processing your request. "
            "Please try again later."
        )

async def main():
    """Start the bot"""
    # Get bot token from environment variable
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("No BOT_TOKEN found in environment variables")
        return
    
    # Log the first few characters of the token for verification
    logger.info(f"Bot token found: {token[:10]}...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Create the Application and pass it your bot's token
        logger.info("Creating application...")
        application = Application.builder().token(token).build()
        logger.info("Application created successfully")
        
        # Add handlers
        logger.info("Adding handlers...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(button))
        logger.info("Handlers added successfully")
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start the Bot
        logger.info("Starting bot polling...")
        await application.initialize()
        await application.start()
        await application.run_polling()
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1) 
