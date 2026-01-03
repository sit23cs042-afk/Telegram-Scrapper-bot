# E-Commerce Discount AI Agent - Setup Guide

## 📁 Project Files

Your Telegram discount aggregator now has 3 main modules:

1. **nlp_discount_parser.py** - NLP module for parsing discount messages
2. **telegram_listener.py** - Telegram integration using Telethon
3. **database.py** - SQLite database for storing deals

---

## 🚀 Quick Start Guide

### Step 1: Install Dependencies

```bash
pip install telethon
```

### Step 2: Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy your **API_ID** and **API_HASH**

### Step 3: Configure API Credentials

**Option A: Environment Variables (Recommended)**
```bash
# Windows PowerShell
$env:TELEGRAM_API_ID="12345678"
$env:TELEGRAM_API_HASH="your_api_hash_here"

# Linux/Mac
export TELEGRAM_API_ID="12345678"
export TELEGRAM_API_HASH="your_api_hash_here"
```

**Option B: Edit telegram_listener.py**
```python
API_ID = '12345678'  # Replace with your API_ID
API_HASH = 'your_api_hash_here'  # Replace with your API_HASH
```

### Step 4: Configure Target Channels

Edit the `TARGET_CHANNELS` list in telegram_listener.py:

```python
TARGET_CHANNELS = [
    'amazon_deals',           # Example channel
    'flipkart_offers',        # Add your channels here
    'loot_deals_india',
    # Add more...
]
```

**How to find channel usernames:**
- Open Telegram and go to the channel
- Click on channel name → Channel info
- The username is shown as @channelname
- Use the part after @ (e.g., 'amazon_deals')

### Step 5: Run the Bot

**Test mode (without Telegram connection):**
```bash
python telegram_listener.py --test
```

**Live mode (connect to Telegram):**
```bash
python telegram_listener.py
```

---

## 📖 Usage Examples

### Testing Individual Modules

**Test NLP Parser:**
```bash
python nlp_discount_parser.py
```

**Test Database:**
```bash
python database.py
```

**Test Telegram Listener (manual mode):**
```bash
python telegram_listener.py --test
```

### Running the Live Bot

```bash
python telegram_listener.py
```

**First time setup:**
1. You'll be prompted to log in
2. Enter your phone number (with country code, e.g., +91xxxxxxxxxx)
3. Enter the code sent to your Telegram app
4. If you have 2FA, enter your password
5. Bot will start listening to channels

**Subsequent runs:**
- Session is saved, so you won't need to log in again
- Just run the script and it starts listening immediately

---

## 🗄️ Database Usage

The bot automatically saves deals to `discount_deals.db`.

### Query the Database

```python
from database import get_recent_deals, get_deals_by_store, get_statistics

# Get 10 most recent deals
deals = get_recent_deals(10)

# Get Amazon deals
amazon_deals = get_deals_by_store('Amazon', limit=20)

# Get fashion deals
fashion_deals = get_deals_by_category('fashion', limit=15)

# Get statistics
stats = get_statistics()
print(f"Total deals: {stats['total_deals']}")
```

---

## 🔧 Configuration Options

### telegram_listener.py

```python
# Session file name
SESSION_NAME = 'discount_bot_session'

# Enable debug logging
ENABLE_DEBUG_LOGGING = True

# Target channels
TARGET_CHANNELS = [...]
```

### database.py

```python
# Database file name
DATABASE_FILE = 'discount_deals.db'
```

---

## 📊 Features

### NLP Parser (nlp_discount_parser.py)
✅ Extracts product title  
✅ Identifies store (Amazon, Flipkart, Myntra, etc.)  
✅ Extracts MRP, discount price, and percentage  
✅ Finds product links  
✅ Auto-categorizes products (electronics, fashion, etc.)  
✅ Removes emojis and cleans text  
✅ Handles multiple price formats (₹, Rs, INR)

### Telegram Listener (telegram_listener.py)
✅ User client (can read all public channels)  
✅ Multi-channel monitoring  
✅ Real-time message processing  
✅ Async event handling  
✅ Comprehensive error handling  
✅ Statistics tracking  
✅ Debug logging  
✅ Manual testing mode

### Database (database.py)
✅ SQLite storage  
✅ Automatic deduplication  
✅ Indexed queries  
✅ Statistics functions  
✅ Query by store/category  
✅ Recent deals retrieval

---

## 🛠️ Troubleshooting

### "API_ID and API_HASH not configured"
- Make sure you've set the environment variables or edited the config

### "No channels are accessible"
- Join the channels on your Telegram account first
- Make sure channel usernames are correct (without @)
- Some channels may be private - you need to be a member

### "Database module not available"
- Make sure database.py is in the same directory
- Check if the file has any syntax errors

### "Module 'telethon' not found"
- Run: `pip install telethon`

---

## 📈 Next Steps

1. **Add more channels** to TARGET_CHANNELS
2. **Create a web dashboard** to view deals
3. **Add notification system** (email/push notifications)
4. **Implement filtering** by price range, category, etc.
5. **Add deal expiry tracking**
6. **Create analytics dashboard**

---

## 🔒 Security Notes

- Never commit your API_ID and API_HASH to version control
- Keep your session file private (it contains authentication tokens)
- Add to .gitignore:
  ```
  *.session
  *.session-journal
  discount_deals.db
  .env
  ```

---

## 📝 Example Output

When running the bot, you'll see:

```
[2025-12-12 14:30:15] [INFO] ✅ Successfully logged in as: Your Name (@username)
[2025-12-12 14:30:16] [INFO] ✅ 5/5 channels accessible
[2025-12-12 14:30:16] [INFO] 👂 Listening to 5 channels...

[2025-12-12 14:30:45] [INFO] 📨 New message from: amazon_deals
[2025-12-12 14:30:45] [INFO] 🤖 Parsing message with NLP...
[2025-12-12 14:30:45] [INFO] 📊 PARSED DATA:
[2025-12-12 14:30:45] [INFO]   title             : Boat Airdopes 441
[2025-12-12 14:30:45] [INFO]   store             : Amazon
[2025-12-12 14:30:45] [INFO]   mrp               : 2999
[2025-12-12 14:30:45] [INFO]   discount_price    : 999
[2025-12-12 14:30:45] [INFO]   discount_percent  : 67
[2025-12-12 14:30:45] [INFO]   link              : https://amzn.to/xxxx
[2025-12-12 14:30:45] [INFO]   category          : electronics
[2025-12-12 14:30:45] [INFO] 💾 Saved to database (Total saved: 1)
```

---

## 🎯 Project Complete!

Your AI agent is now ready to:
1. ✅ Monitor Telegram channels 24/7
2. ✅ Parse discount messages using NLP
3. ✅ Extract structured product data
4. ✅ Save to database automatically
5. ✅ Handle errors gracefully

**Happy deal hunting! 🎉**
