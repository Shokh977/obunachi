import asyncio
import logging
import os
import json
import re
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandObject, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "sahifalab1")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
LINKS_DB_PATH = "links_db.json"

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Get bot username for generating links
BOT_USERNAME = None

# ========================
# LINK DATABASE MANAGER
# ========================
class LinkManager:
    """Manage link mappings in JSON"""
    
    @staticmethod
    def load_links():
        """Load links from database"""
        try:
            if os.path.exists(LINKS_DB_PATH):
                with open(LINKS_DB_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading links_db.json: {e}")
            return {}
    
    @staticmethod
    def save_links(links_dict):
        """Save links to database"""
        try:
            with open(LINKS_DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(links_dict, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving links_db.json: {e}")
            return False
    
    @staticmethod
    def add_link(message_id, post_url):
        """Add new link mapping"""
        links = LinkManager.load_links()
        links[str(message_id)] = post_url
        return LinkManager.save_links(links)
    
    @staticmethod
    def get_link(message_id):
        """Get post URL by message_id"""
        links = LinkManager.load_links()
        return links.get(str(message_id), None)


# ========================
# HELPER FUNCTIONS
# ========================
def extract_message_id(url):
    """Extract message ID from Telegram URL"""
    # Match patterns like https://t.me/channel/12345
    match = re.search(r't\.me/[^/]+/(\d+)', url)
    if match:
        return match.group(1)
    return None


async def check_subscription(user_id: int, channel_username: str) -> bool:
    """Check if user is subscribed to channel"""
    try:
        # Username-dagi @ belgisini tozalab, o'zimiz bitta qo'shamiz
        clean_username = channel_username.replace("@", "")
        chat_member = await bot.get_chat_member(chat_id=f"@{clean_username}", user_id=user_id)
        
        # Statuslarni tekshirish
        allowed_statuses = ["member", "administrator", "creator"]
        return chat_member.status in allowed_statuses
    except Exception as e:
        error_str = str(e)
        
        # Agar kanal topilmasa - adminni ogohlantir
        if "chat not found" in error_str.lower():
            logger.critical(
                f"🚨 CRITICAL: Bot MUST be administrator in @{channel_username}. "
                f"Add the bot to the channel and give it admin rights."
            )
        else:
            logger.error(f"Error checking subscription for @{channel_username}: {e}")
        
        return False


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID


# ========================
# COMMAND HANDLERS
# ========================
@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    """Handle /start command with optional message_id (User Flow)"""
    
    user_id = message.from_user.id
    message_id = command.args
    
    logger.info(f"User {user_id} started with message_id: {message_id}")
    
    # If no message_id provided - welcome message
    if not message_id:
        await message.answer(
            "Assalomu alaykum! 👋 Men Samman.\n\n"
            "SAHIFALAB YouTube kanalining videolarining "
            "foydalı materiallari shu bot orqali taqdim etiladi. 😊\n\n"
            "Videoning tavsifida berilgan linkni bosing!"
        )
        return
    
    # Get original link from database
    original_link = LinkManager.get_link(message_id)
    if not original_link:
        await message.answer(
            "Assalomu alaykum! Kechirasiz, bu material bazada yo'q. 🧐"
        )
        logger.warning(f"Message ID '{message_id}' not found in database")
        return
    
    # Check subscription
    is_member = await check_subscription(user_id, CHANNEL_USERNAME)
    
    if is_member:
        # ✅ User is subscribed - show the link button
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="📄 Materialni ko'rish",
            url=original_link
        ))
        
        await message.answer(
            "Assalomu alaykum! Ajoyib tanlov. 🎉\n\n"
            "Mana siz so'ragan material:",
            reply_markup=builder.as_markup()
        )
        logger.info(f"User {user_id} is subscribed - material shown for message_id: {message_id}")
    else:
        # ❌ User is not subscribed - show join and verify buttons
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="📢 Kanalga obuna bo'lish",
            url=f"https://t.me/{CHANNEL_USERNAME}"
        ))
        builder.row(types.InlineKeyboardButton(
            text="✅ Tekshirish",
            callback_data=f"verify_{message_id}"
        ))
        
        await message.answer(
            "Assalomu alaykum! 😊\n\n"
            "Foydali materialni yuklashdan oldin kanalimizga obuna bo'lishingizni so'rayman. "
            "Bu bizga yangi videolar uchun kuch beradi!",
            reply_markup=builder.as_markup()
        )
        logger.info(f"User {user_id} not subscribed - join prompt shown")


@dp.message(F.text.startswith("https://t.me/"))
async def handle_admin_link(message: types.Message):
    """Handle admin link submission (Admin Flow)"""
    
    user_id = message.from_user.id
    
    # ✅ ADMIN FLOW: Check if user is admin
    if not is_admin(user_id):
        await message.answer(
            "Assalomu alaykum! Kechirasiz, bu funksiya faqat admin uchun. 🚫"
        )
        logger.warning(f"Non-admin user {user_id} tried to submit link")
        return
    
    # Extract message ID from URL
    message_id = extract_message_id(message.text)
    if not message_id:
        await message.answer(
            "Assalomu alaykum! Linkni to'g'ri formatda yuboring.\n\n"
            "✅ Misol:\n`https://t.me/sahifalab1/12345`",
            parse_mode="Markdown"
        )
        return
    
    # Save to database
    if LinkManager.add_link(message_id, message.text):
        # Get bot username for generating link
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        
        generated_link = f"https://t.me/{bot_username}?start={message_id}"
        
        await message.answer(
            "Assalomu alaykum! 🖐 Men Samman.\n\n"
            "Material bazaga qo'shildi. ✅\n\n"
            "Videongiz ostiga mana bu linkni qo'ying:\n\n"
            f"`{generated_link}`",
            parse_mode="Markdown"
        )
        logger.info(f"Admin {user_id} added link: message_id={message_id}")
    else:
        await message.answer(
            "Assalomu alaykum! Xatolik yuz berdi. Qayta urinib ko'ring. ❌"
        )


# ========================
# CALLBACK HANDLERS
# ========================
@dp.callback_query(F.data.startswith("verify_"))
async def callback_verify_subscription(callback: types.CallbackQuery):
    """Handle subscription verification button (User verifies after joining)"""
    
    user_id = callback.from_user.id
    message_id = callback.data.split("_", 1)[1]
    
    logger.info(f"User {user_id} clicked verify for message_id: {message_id}")
    
    # Re-check subscription
    is_member = await check_subscription(user_id, CHANNEL_USERNAME)
    
    if is_member:
        # ✅ User just subscribed - EDIT message to show material button
        original_link = LinkManager.get_link(message_id)
        if not original_link:
            await callback.answer("Xatolik yuz berdi!", show_alert=True)
            return
        
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="📄 Materialni ko'rish",
            url=original_link
        ))
        
        await callback.message.edit_text(
            "Assalomu alaykum! Ajoyib tanlov. 🎉\n\n"
            "Mana siz so'ragan material:",
            reply_markup=builder.as_markup()
        )
        await callback.answer("Shukriyalar! Siz kanalga obuna bo'lgansiz! ✅", show_alert=False)
        logger.info(f"User {user_id} verified and now subscribed")
    else:
        # ❌ Still not subscribed
        await callback.answer(
            "Hali kanalga obuna bo'lmagansiz. Iltimos, avval obuna bo'ling!",
            show_alert=True
        )
        logger.info(f"User {user_id} still not subscribed")


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
    
    logger.info("🤖 SAHIFALAB Bot (Sam - Link Generator & Subscription Checker) started!")
    logger.info(f"📢 Channel: @{CHANNEL_USERNAME}")
    logger.info(f"👤 Admin ID: {ADMIN_ID}")
    logger.info("✅ Ready to process links and verify subscriptions...")
    
    # Reset webhook
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close() if bot.session else None


if __name__ == "__main__":
    asyncio.run(main())