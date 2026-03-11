# SAHIFALAB Bot Upgrade - Complete Documentation

## 🎯 What's New

Your SAHIFALAB bot has been upgraded from hardcoded file mappings to a **professional JSON-based storage system** with **admin control panel**.

---

## 📋 Key Changes

### ❌ Old System
```python
FILES_MAP = {
    "atom_odatlar": "https://t.me/sahifalab/10",
    "deep_work": "https://t.me/sahifalab/11",
}
```
❌ Had to modify code to add files  
❌ Needed bot restart  
❌ Not scalable  

### ✅ New System
```json
{
  "atom_odatlar": "https://t.me/sahifalab/10",
  "deep_work": "https://t.me/sahifalab/11"
}
```
✅ Add files via `/add` command  
✅ Instant updates (no restart!)  
✅ Professional & scalable  

---

## 🏗️ Architecture

### FileManager Class
```python
class FileManager:
    @staticmethod
    def load_files()          # Read files.json
    @staticmethod
    def save_files(dict)      # Write to files.json
    @staticmethod
    def add_file(id, url)     # Add new mapping
    @staticmethod
    def get_file(id)          # Retrieve URL by ID
```

**Flow:**
1. `/start file_id` → Call `FileManager.get_file(file_id)`
2. Admin `/add file_id url` → Call `FileManager.add_file(file_id, url)`
3. All operations → Read/write `files.json`

---

## ⚙️ Configuration

### .env File (IMPORTANT!)
```dotenv
BOT_TOKEN=8723261758:AAGbA3Irhob3cC_9gM1avzcM741PAbMxAIY
CHANNEL_USERNAME=@sahifalab1
ADMIN_ID=123456789
```

**Must Update:**
- `ADMIN_ID=123456789` → Replace with YOUR Telegram user ID
  - Get it from @userinfobot on Telegram
  - Must be a number (not username!)

### files.json Structure
```json
{
  "atom_odatlar": "https://t.me/sahifalab/10",
  "deep_work": "https://t.me/sahifalab/11",
  "calculus": "https://t.me/sahifalab/12"
}
```

Keys = file_id (used in `/start file_id`)  
Values = Telegram post URLs

---

## 🚀 Usage Guide

### For Users

**Step 1:** Get YouTube link from your channel description
```
https://t.me/Sahifalab_obunachi_bot?start=atom_odatlar
```

**Step 2:** User clicks link
- ✅ If subscribed to @sahifalab1 → See "Download PDF" button
- ❌ If not subscribed → See "Join Channel" + "Verify" buttons

**Step 3:** After joining → Click "Verify" → Get download link

---

### For Admin (You!)

#### Add New File
```
/add atom_odatlar https://t.me/sahifalab/10
```

**What happens:**
1. Bot validates: Are you admin? (Checks ADMIN_ID)
2. Bot adds to `files.json`: `"atom_odatlar": "https://..."`
3. Bot sends: "✅ Sam: Muvaffaqiyat! Yangi link ma'lumotlar bazasiga qo'shildi. ✅"
4. **Instantly available!** No restart needed

#### View Current Files
Edit `files.json` manually or use a JSON viewer

#### Remove File
Edit `files.json` and delete the line, save

---

## 💬 All Bot Messages (Uzbek)

### User Messages

| Trigger | Response |
|---------|----------|
| `/start` (no file_id) | "Salom! 👋 Men Samman. SAHIFALAB YouTube..." |
| `/start invalid_id` | "❌ Kechirasiz, so'ragan faylni topa olmadim..." |
| Not subscribed | "Assalomu alaykum! PDF-ni yuklab olishingiz uchun..." |
| Is subscribed | "Ajoyib! Siz biz bilan ekansiz. 🎉 Mana siz so'ragan material:" |
| Clicks "Verify" + subscribed | "✅ Shukriyalar! Siz kanalga obuna bo'lgansiz!" |
| Clicks "Verify" + not subscribed | "Hali kanalga obuna bo'lmagansiz. Iltimos, avval..." |

### Admin Messages

| Command | Response | Condition |
|---------|----------|-----------|
| `/add file_id url` | "✅ Sam: Muvaffaqiyat!..." | Success |
| `/add file_id url` | "❌ Sam: Xatolik yuz berdi!..." | Save failed |
| `/add` (non-admin) | "🚫 Kechirasiz, bu buyruq faqat admin uchun!..." | Not admin |
| `/add` (no args) | "📝 Foydalanish: /add file_id post_url..." | Missing args |

---

## 🔐 Security Features

✅ **Admin-Only Commands**
```python
def is_admin(user_id):
    return user_id == ADMIN_ID
```
Only ADMIN_ID from .env can use `/add`

✅ **Real Subscription Check**
- Validates against actual Telegram API
- Not cached (live verification)

✅ **Error Handling**
- File I/O errors caught
- API failures logged
- Bot continues running

✅ **Logging**
- All admin actions logged
- User access tracked
- Errors documented

---

## 📊 File Operations

### Load Files
```python
files = FileManager.load_files()
# Returns: {"atom_odatlar": "https://...", ...}
```

### Save Files
```python
FileManager.save_files(files)
# Writes to files.json with UTF-8 encoding
```

### Add New File
```python
FileManager.add_file("calculus", "https://t.me/sahifalab/12")
# Loads → adds → saves all in one call
```

### Get File URL
```python
url = FileManager.get_file("atom_odatlar")
# Returns: "https://t.me/sahifalab/10"
```

---

## 📝 Complete Workflow Example

### Scenario: Add New Course Material

**Step 1:** Upload PDF to Telegram channel
- Post it in @sahifalab1
- Get link: `https://t.me/sahifalab/15`

**Step 2:** Send admin command to bot
```
/add calculus_basics https://t.me/sahifalab/15
```

**Step 3:** Bot responds
```
✅ Sam: Muvaffaqiyat! Yangi link ma'lumotlar bazasiga qo'shildi. ✅
```

**Step 4:** Check files.json (now contains)
```json
{
  ...existing files...,
  "calculus_basics": "https://t.me/sahifalab/15"
}
```

**Step 5:** Update YouTube description
```
📚 Calculus Basics: https://t.me/Sahifalab_obunachi_bot?start=calculus_basics
```

**Step 6:** Users can now access!
- Click link → Auto-checked → Download PDF

---

## 🐛 Troubleshooting

### Problem: "ValueError: invalid literal for int() with base 10"
**Solution:** ADMIN_ID in .env is invalid
- Must be a number: `ADMIN_ID=123456789`
- NOT a username: `ADMIN_ID=@username` ❌

### Problem: "Conflict: terminated by other getUpdates request"
**Solution:** Old bot session still active on Telegram
1. Kill all Python: `Get-Process python | Stop-Process -Force`
2. Wait 60+ seconds
3. Restart bot

### Problem: `/add` command doesn't work
**Solution:** Check three things:
1. Is your ADMIN_ID correct in .env?
2. Are you sending: `/add file_id url` (with space)?
3. Is `files.json` writable?

### Problem: File not found error when user accesses `/start file_id`
**Solution:**
1. Check `files.json` exists
2. Verify file_id matches exactly (case-sensitive!)
3. JSON format is valid (use online JSON validator)

---

## 📂 Project Structure

```
Obunabot/
├── main.py              # Bot code (190 lines)
│   ├── FileManager class
│   ├── @dp.message(Command("start"))
│   ├── @dp.message(Command("add"))
│   └── @dp.callback_query handlers
│
├── files.json           # File mappings (4 entries example)
├── .env                 # Config (3 variables)
├── requirements.txt     # 2 packages
├── README.md           # Quick reference
└── UPGRADE.md          # This file
```

---

## 🔄 Data Flow Diagrams

### User Access Flow
```
User clicks /start atom_odatlar
    ↓
FileManager.get_file("atom_odatlar")
    ↓
Load files.json
    ↓
Return URL (or None if not found)
    ↓
Check subscription
    ↓
Show PDF button or "Join" prompt
```

### Admin Add File Flow
```
Admin sends: /add atom_odatlar https://...
    ↓
Check: is_admin(user_id)?
    ↓
Parse: file_id = "atom_odatlar", url = "https://..."
    ↓
FileManager.add_file(file_id, url)
    ↓
Load files.json
    ↓
Add entry
    ↓
Save to files.json
    ↓
Send "✅ Success!" message
```

---

## 🎓 Key Improvements

### Before (Hardcoded)
- ❌ Add file → Edit code → Restart bot
- ❌ Each restart = service interruption
- ❌ Risk of syntax errors
- ❌ Not scalable (50+ files = messy code)

### After (JSON + Admin Command)
- ✅ Add file → Send `/add` command → Instant
- ✅ Zero downtime
- ✅ No code changes
- ✅ Scales to 1000+ files
- ✅ Professional setup

---

## ✨ Sam's Personality

All messages maintain Sam's character:
- 🎉 Friendly & motivational tone
- 📢 Encourages channel subscription
- ✅ Celebratory confirmations
- 💬 Uzbek language always
- 😊 Emoji use throughout

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start bot | `python main.py` |
| Add file | `/add file_id https://...` |
| View files | Edit `files.json` |
| Check logs | Look at console output |
| Restart bot | Kill Python + start again |
| Update admin | Change `ADMIN_ID` in `.env` |

---

## 🎯 Next Steps

1. **Update ADMIN_ID** in `.env` with your real ID
2. **Start the bot**: `python main.py`
3. **Test add command**: `/add test_file https://t.me/sahifalab/1`
4. **Verify files.json** was updated
5. **Add to YouTube** description links like: `https://t.me/bot?start=file_id`

---

**Your SAHIFALAB bot is now professional-grade! 🚀**

Questions? Check bot logs for details on any operation.
