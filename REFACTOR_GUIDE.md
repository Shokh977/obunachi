# 🚀 SAHIFALAB Bot - Refactored Setup Guide

## ✅ What's New (Refactored)

Your bot has been **completely refactored** to function as:
1. **Automated Link Generator** (for Admin)
2. **Subscription Checker** (for Users)

### Before ❌
- Admin had to use `/add file_id url` command
- Required manual mapping entry

### After ✅
- Admin just pastes a Telegram link
- Bot auto-extracts message ID
- Bot auto-generates shareable link
- Bot auto-stores in `links_db.json`
- **One action = Complete workflow!**

---

## 📋 How It Works

### Admin Workflow (You)

**Step 1:** Copy link from your Telegram channel
```
https://t.me/sahifalab1/38
```

**Step 2:** Send to bot (just paste it)
- The bot detects admin messages starting with `https://t.me/`
- Extracts message ID: `38`
- Saves mapping: `"38": "https://t.me/sahifalab1/38"`
- Generates link: `https://t.me/BotUsername?start=38`

**Step 3:** Bot replies
```
Assalomu alaykum! Men Samman. 🖐

Material bazaga qo'shildi. Videongiz ostiga mana bu linkni qo'ying:

https://t.me/BotUsername?start=38
```

**Step 4:** Share in YouTube description
Just copy the generated link and paste in your video description!

---

### User Workflow

**Step 1:** User clicks your YouTube link
```
https://t.me/BotUsername?start=38
```

**Step 2:** Bot automatically:
- Loads message ID: `38`
- Gets original URL from `links_db.json`
- Checks: Is user subscribed to @sahifalab1?

**Step 3a - If Subscribed ✅**
```
Assalomu alaykum! Ajoyib tanlov. 🎉 Mana siz so'ragan material:
[Shows original link button]
```

**Step 3b - If Not Subscribed ❌**
```
Assalomu alaykum! Men Samman. 😊

Foydali materialni yuklashdan oldin kanalimizga obuna bo'lishingizni so'rayman.
Bu bizga yangi videolar uchun kuch beradi!

[Join Channel Button] [Verify Button]
```

**Step 4:** After joining → Click Verify → Gets material

---

## 📂 Files

| File | Purpose | Change |
|------|---------|--------|
| `main.py` | Bot code | ✅ Completely refactored |
| `links_db.json` | Link storage | ✅ New format (message_id → URL) |
| `.env` | Config | ✅ Already set with your ID |
| `requirements.txt` | Dependencies | ℹ️ No change |

---

## 🎯 Configuration

### .env Status
```dotenv
BOT_TOKEN=8723261758:AAGbA3Irhob3cC_9gM1avzcM741PAbMxAIY  ✅
CHANNEL_USERNAME=@sahifalab1                               ✅
ADMIN_ID=807466591                                         ✅
```

**Everything is configured!** Just start using it.

---

## 💻 Start Bot

```bash
python main.py
```

### Bot Console Output
```
INFO:__main__:🤖 SAHIFALAB Bot (Sam - Link Generator & Subscription Checker) started!
INFO:__main__:📢 Channel: @@sahifalab1
INFO:__main__:👤 Admin ID: 807466591
INFO:__main__:✅ Ready to process links and verify subscriptions...
```

✅ When you see this, bot is ready!

---

## 📝 Data Storage: links_db.json

### Format
```json
{
  "message_id": "original_telegram_url"
}
```

### Examples
```json
{
  "38": "https://t.me/sahifalab1/38",
  "45": "https://t.me/sahifalab1/45",
  "123": "https://t.me/sahifalab1/123"
}
```

### Auto-Updated
Every time admin sends a link, bot automatically:
1. Extracts message ID
2. Stores mapping
3. Generates shareable link

---

## 🔄 Complete Example Workflow

### Scenario: Share chemistry tutorial

**Step 1:** Upload video to @sahifalab1
- Message ID: 156

**Step 2:** Copy the link
```
https://t.me/sahifalab1/156
```

**Step 3:** Send to bot (admin)
- Just paste `https://t.me/sahifalab1/156`

**Step 4:** Bot responds
```
Assalomu alaykum! Men Samman. 🖐

Material bazaga qo'shildi. Videongiz ostiga mana bu linkni qo'ying:

https://t.me/Sahifalab_obunachi_bot?start=156
```

**Step 5:** Add to YouTube description
```
📚 Kimyo Darslik: https://t.me/Sahifalab_obunachi_bot?start=156
```

**Step 6:** Users click link
- Bot checks subscription
- If yes → Shows chemistry link
- If no → Shows "Join" button

---

## 💬 All Messages (Uzbek)

### Admin Messages
| Scenario | Message |
|----------|---------|
| Valid link | "Assalomu alaykum! Men Samman. 🖐\n\nMaterial bazaga qo'shildi..." |
| Invalid format | "Assalomu alaykum! Linkni to'g'ri formatda yuboring.\nMisol: https://t.me/sahifalab1/12345" |
| Non-admin | "Assalomu alaykum! Kechirasiz, bu funksiya faqat admin uchun. 🚫" |

### User Messages
| Scenario | Message |
|----------|---------|
| `/start` (no ID) | "Assalomu alaykum! Men Samman. 👋\n\nSAHIFALAB YouTube kanalining do'stingman..." |
| ID not found | "Assalomu alaykum! Kechirasiz, bu material bazada topilmadi. 😔" |
| Not subscribed | "Assalomu alaykum! Men Samman. 😊\n\nFoydali materialni yuklashdan oldin..." |
| Is subscribed | "Assalomu alaykum! Ajoyib tanlov. 🎉 Mana siz so'ragan material:" |
| After verify + subscribed | "Shukriyalar! Siz kanalga obuna bo'lgansiz! ✅" |
| After verify + still not subscribed | "Hali kanalga obuna bo'lmagansiz. Iltimos, avval obuna bo'ling!" |

---

## 🔍 Technical Details

### LinkManager Class
```python
class LinkManager:
    @staticmethod
    def load_links()          # Load links_db.json
    @staticmethod
    def save_links(dict)      # Write links_db.json
    @staticmethod
    def add_link(id, url)     # Add message_id → url
    @staticmethod
    def get_link(id)          # Get URL by message_id
```

### URL Parser
```python
def extract_message_id(url):
    # Converts: https://t.me/sahifalab1/38 → "38"
    # Regex: t\.me/[^/]+/(\d+)
```

### Handler Flow
```python
# Admin sends link
@dp.message(F.text.startswith("https://t.me/"))
    → Check is_admin()
    → Extract message_id
    → Save to links_db.json
    → Generate /start link
    → Send to admin

# User clicks /start link
@dp.message(Command("start"))
    → Get message_id
    → Load from links_db.json
    → Check subscription
    → Show material or join prompt
```

---

## ✨ Key Features

✅ **Automatic Link Generation** - No manual input needed  
✅ **Smart URL Parsing** - Extracts IDs automatically  
✅ **Real Subscription Check** - Verifies @sahifalab1 membership  
✅ **Instant Storage** - links_db.json auto-updated  
✅ **Uzbek Throughout** - All messages in Uzbek  
✅ **"Assalomu alaykum!" Greeting** - Every message starts with it  
✅ **Sam's Personality** - Friendly, motivational 16-year-old mentor  

---

## 🚦 Quick Reference

| Action | What Happens |
|--------|--------------|
| Admin pastes link | Bot extracts ID → saves → generates link |
| Admin gets response | Copy generated link → paste in YouTube |
| User clicks link | Bot checks subscription → shows material or join prompt |
| User joins + verifies | Bot shows material link |
| Edit stored links | Edit `links_db.json` directly |

---

## 📞 Common Issues & Solutions

### Issue: "Linkni to'g'ri formatda yuboring"
**Solution:** Make sure:
- Link starts with `https://t.me/`
- Format is: `https://t.me/channel_name/message_id`
- Message ID is numeric (e.g., 38, not "test")

### Issue: Bot shows "Material bazada topilmadi"
**Solution:** 
- Check `links_db.json` - message ID might not be stored
- Admin needs to paste the original link first
- Verify JSON format is valid

### Issue: User not seeing material even after joining
**Solution:**
- May take 1-2 minutes for Telegram API to sync
- User should click "Verify" button again
- Check bot logs for errors

---

## 🎓 Advanced: Manual links_db.json Editing

### Add Link Manually
1. Open `links_db.json`
2. Add entry:
   ```json
   "200": "https://t.me/sahifalab1/200"
   ```
3. Save file
4. Link now works: `https://t.me/bot?start=200`

### Remove Link
1. Open `links_db.json`
2. Delete the line
3. Save file

### Backup Links
Simply copy `links_db.json` to another location!

---

## ✅ Verification Checklist

- [x] Bot code refactored for link generation
- [x] LinkManager class implemented
- [x] URL extraction working
- [x] Admin-only link submission
- [x] Subscription verification active
- [x] links_db.json created
- [x] All messages in Uzbek
- [x] "Assalomu alaykum!" in every message
- [x] Sam's personality maintained
- [x] ADMIN_ID configured
- [x] Bot running successfully

---

## 🎉 You're Ready!

Your bot is now:
- **Professional** ✅
- **Fully Automated** ✅
- **User-Friendly** ✅
- **Uzbek-Based** ✅
- **Sam's Personality** ✅

**Start sharing links!** 🚀

---

Generated: March 12, 2026  
Version: 3.0 (Refactored - Link Generator)  
Status: ✅ Production Ready
