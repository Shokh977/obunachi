import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.client.session import aiohttp_session

from file_mapping import get_post_url

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========================
# UZBEK MESSAGES
# ========================
MESSAGES = {
    "greeting_not_member": (
        "Assalomu alaykum! PDF-ni yuklab olishingiz uchun "
        "\"SAHIFALAB\" kanalimizga obuna bo'lishingiz kerak. "
        "Bu bizga yangi videolar tayyorlashda katta yordam beradi! 😊"
    ),
    "greeting_member": (
        "Ajoyib! Siz biz bilan ekansiz. 🎉 Mana siz so'ragan kitob materiallari joylashgan post:"
    ),
    "not_member": "Siz hali kanalga obuna bo'lmagansiz. Iltimos, avval obuna bo'ling!",
    "error_checking": "Obunani tekshirishda xatolik yuz berdi. Keyinroq urinib ko'ring.",
    "file_not_found": "Kechirasiz, so'ragan faylni topa olmadim 😔",
    "welcome_message": "Salom! 👋 SAHIFALAB botiga xush kelibsiz! PDF-larni yuklash uchun /start buyrug'idan foydalaning.",
}

# Uzbek Button Labels
BUTTONS = {
    "join_channel": "Kanalga a'zo bo'lish",
    "check_subscription": "Obunani tekshirish",
    "view_pdf": "PDF-ni ko'rish",
}


# ========================
# HELPER FUNCTIONS
# ========================
async def check_user_subscription(user_id: int, channel_username: str) -> bool:
    """
    Check if user is a member of the channel
    Returns True if member, False otherwise
    """
    try:
        channel_member = await bot.get_chat_member(
            chat_id=f"@{channel_username}",
            user_id=user_id
        )
        
        # Check if user is member (status can be 'member', 'administrator', 'creator', etc.)
        return channel_member.status in ["member", "administrator", "creator", "restricted"]
    except Exception as e:
        logger.error(f"Error checking subscription for user {user_id}: {e}")
        return False


def get_join_channel_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for non-members"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=BUTTONS["join_channel"],
                url=f"https://t.me/{CHANNEL_USERNAME}"
            )],
            [InlineKeyboardButton(
                text=BUTTONS["check_subscription"],
                callback_data="check_sub"
            )]
        ]
    )
    return keyboard


def get_view_pdf_keyboard(post_url: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for members"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=BUTTONS["view_pdf"],
                url=post_url
            )]
        ]
    )
    return keyboard


# ========================
# COMMAND HANDLERS
# ========================
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Handle /start command with optional file_id parameter"""
    
    user_id = message.from_user.id
    command_args = message.text.split()
    
    # Check if file_id was provided
    file_id: Optional[str] = None
    if len(command_args) > 1:
        file_id = command_args[1]
    
    # Log user interaction
    logger.info(f"User {user_id} started bot with file_id: {file_id}")
    
    # If no file_id, show welcome message
    if not file_id:
        await message.answer(MESSAGES["welcome_message"])
        return
    
    # Check if file exists in mapping
    post_url = get_post_url(file_id)
    if not post_url:
        await message.answer(MESSAGES["file_not_found"])
        return
    
    # Check subscription status
    is_member = await check_user_subscription(user_id, CHANNEL_USERNAME)
    
    if is_member:
        # User is a member - show the post
        await message.answer(
            MESSAGES["greeting_member"],
            reply_markup=get_view_pdf_keyboard(post_url)
        )
        logger.info(f"User {user_id} is member - showing PDF for file_id: {file_id}")
    else:
        # User is not a member - ask to subscribe
        await message.answer(
            MESSAGES["greeting_not_member"],
            reply_markup=get_join_channel_keyboard()
        )
        logger.info(f"User {user_id} is not member - asking to subscribe")


# ========================
# CALLBACK HANDLERS
# ========================
@dp.callback_query(F.data == "check_sub")
async def check_subscription_handler(callback_query: types.CallbackQuery):
    """Handle subscription check button click"""
    
    user_id = callback_query.from_user.id
    
    # Check subscription status
    is_member = await check_user_subscription(user_id, CHANNEL_USERNAME)
    
    if is_member:
        await callback_query.answer("Shukriyalar! Siz kanalga obuna bo'lgansiz! ✅", show_alert=False)
        # Optionally, here you can trigger file sending or next action
        # For now, we just acknowledge
    else:
        await callback_query.answer(MESSAGES["not_member"], show_alert=True)
    
    await callback_query.answer()


# ========================
# ERROR HANDLER
# ========================
@dp.error()
async def error_handler(update, exception):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {exception}")


# ========================
# MAIN FUNCTION
# ========================
async def main():
    """Main function to run the bot"""
    
    logger.info("🤖 SAHIFALAB Bot started!")
    logger.info(f"📢 Channel: @{CHANNEL_USERNAME}")
    
    try:
        # Start polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
