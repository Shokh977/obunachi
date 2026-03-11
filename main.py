import asyncio
import logging
import os
import json
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandObject, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "sahifalab")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
FILES_JSON_PATH = "files.json"

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========================
# JSON FILE MANAGER
# ========================
class FileManager:
    """Manage file mappings in JSON"""
    
    @staticmethod
    def load_files():
        """Load file mappings from JSON"""
        try:
            if os.path.exists(FILES_JSON_PATH):
                with open(FILES_JSON_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading files.json: {e}")
            return {}
    
    @staticmethod
    def save_files(files_dict):
        """Save file mappings to JSON"""
        try:
            with open(FILES_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(files_dict, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving files.json: {e}")
            return False
    
    @staticmethod
    def add_file(file_id, post_url):
        """Add new file mapping"""
        files = FileManager.load_files()
        files[file_id] = post_url
        return FileManager.save_files(files)
    
    @staticmethod
    def get_file(file_id):
        """Get post URL by file_id"""
        files = FileManager.load_files()
        return files.get(file_id, None)


# ========================
# UZBEK MESSAGES
# ========================
MESSAGES = {
    "welcome": "Salom! 👋 Men Samman. SAHIFALAB YouTube kanalining endi xush ko'rishni istaydigan do'stingman! 😊",
    "not_member": (
        "Assalomu alaykum! PDF-ni yuklab olishingiz uchun 'SAHIFALAB' kanalimizga obuna bo'lishingiz kerak. "
        "Bu bizga yangi videolar tayyorlashda katta yordam beradi! 😊"
    ),
    "member": "Ajoyib! Siz biz bilan ekansiz. 🎉 Mana siz so'ragan material:",
    "verified": "Shukriyalar! Siz kanalga obuna bo'lgansiz! ✅",
    "still_not_member": "Hali kanalga obuna bo'lmagansiz. Iltimos, avval 'Kanalga a'zo bo'lish' tugmasini bosing!",
    "file_not_found": "❌ Kechirasiz, so'ragan faylni topa olmadim. Iltimos, to'g'ri linkni ishlating!",
    "not_admin": "🚫 Kechirasiz, bu buyruq faqat admin uchun! Sam: Siz admin emassiz! 😔",
    "admin_add_success": "✅ Sam: Muvaffaqiyat! Yangi link ma'lumotlar bazasiga qo'shildi. ✅",
    "admin_add_error": "❌ Sam: Xatolik yuz berdi! Link qo'shib bo'lmadi. Qayta urinib ko'ring.",
    "admin_usage": "📝 Foydalanish: /add file_id post_url\nMisol: /add atom_odatlar https://t.me/sahifalab/10",
}

# ========================
# BUTTON LABELS
# ========================
BUTTONS = {
    "join_channel": "📢 Kanalga a'zo bo'lish",
    "check_sub": "✅ Obunani tekshirish",
    "download_pdf": "📄 PDF-ni yuklab olish",
}


# ========================
# HELPER FUNCTIONS
# ========================
async def check_subscription(user_id: int, channel_username: str) -> bool:
    """Check if user is subscribed to channel"""
    try:
        chat_member = await bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_id)
        return chat_member.status in ["member", "administrator", "creator", "restricted"]
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        return False


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID


# ========================
# COMMAND HANDLERS
# ========================
@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    """Handle /start command with optional file_id"""
    
    user_id = message.from_user.id
    file_id = command.args  # Get file_id from deep link (e.g., /start atom_odatlar)
    
    logger.info(f"User {user_id} started bot with file_id: {file_id}")
    
    # If no file_id provided, show welcome message
    if not file_id:
        await message.answer(MESSAGES["welcome"])
        return
    
    # Check if file_id exists in files.json
    post_url = FileManager.get_file(file_id)
    if not post_url:
        await message.answer(MESSAGES["file_not_found"])
        logger.warning(f"File ID '{file_id}' not found in files.json")
        return
    
    # Check subscription status
    is_member = await check_subscription(user_id, CHANNEL_USERNAME)
    
    if is_member:
        # User is subscribed - show PDF link
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text=BUTTONS["download_pdf"],
            url=post_url
        ))
        
        await message.answer(
            MESSAGES["member"],
            reply_markup=builder.as_markup()
        )
        logger.info(f"User {user_id} is member - PDF shown for file_id: {file_id}")
    else:
        # User is not subscribed - ask to join
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text=BUTTONS["join_channel"],
            url=f"https://t.me/{CHANNEL_USERNAME}"
        ))
        builder.row(types.InlineKeyboardButton(
            text=BUTTONS["check_sub"],
            callback_data=f"check_{file_id}"
        ))
        
        await message.answer(
            MESSAGES["not_member"],
            reply_markup=builder.as_markup()
        )
        logger.info(f"User {user_id} is not member - subscription check offered")


@dp.message(Command("add"))
async def cmd_add_file(message: types.Message, command: CommandObject):
    """Admin command to add new file mapping - /add file_id post_url"""
    
    user_id = message.from_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await message.answer(MESSAGES["not_admin"])
        logger.warning(f"Non-admin user {user_id} tried to use /add command")
        return
    
    # Parse arguments
    args = command.args
    if not args:
        await message.answer(MESSAGES["admin_usage"])
        return
    
    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(MESSAGES["admin_usage"])
        return
    
    file_id, post_url = parts
    
    # Add file to JSON
    if FileManager.add_file(file_id, post_url):
        await message.answer(MESSAGES["admin_add_success"])
        logger.info(f"Admin {user_id} added file: {file_id} -> {post_url}")
    else:
        await message.answer(MESSAGES["admin_add_error"])
        logger.error(f"Failed to add file: {file_id}")


# ========================
# CALLBACK HANDLERS
# ========================
@dp.callback_query(F.data.startswith("check_"))
async def callback_check_subscription(callback: types.CallbackQuery):
    """Handle subscription verification button"""
    
    user_id = callback.from_user.id
    file_id = callback.data.split("_", 1)[1]  # Extract file_id from callback_data
    
    logger.info(f"User {user_id} clicked verify button for file_id: {file_id}")
    
    # Re-check subscription
    is_member = await check_subscription(user_id, CHANNEL_USERNAME)
    
    if is_member:
        # User just subscribed
        post_url = FileManager.get_file(file_id)
        if not post_url:
            await callback.answer("Xatolik yuz berdi. File topilmadi!", show_alert=True)
            return
        
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text=BUTTONS["download_pdf"],
            url=post_url
        ))
        
        await callback.message.edit_text(
            MESSAGES["member"],
            reply_markup=builder.as_markup()
        )
        await callback.answer(MESSAGES["verified"], show_alert=False)
        logger.info(f"User {user_id} verified membership - PDF shown")
    else:
        # Still not subscribed
        await callback.answer(MESSAGES["still_not_member"], show_alert=True)
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
    
    logger.info("🤖 SAHIFALAB Bot (Sam's Version) started!")
    logger.info(f"📢 Channel: @{CHANNEL_USERNAME}")
    logger.info(f"👤 Admin ID: {ADMIN_ID}")
    logger.info("✅ Ready to receive messages...")
    
    # Reset session to clear conflicts
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close() if bot.session else None


if __name__ == "__main__":
    asyncio.run(main())