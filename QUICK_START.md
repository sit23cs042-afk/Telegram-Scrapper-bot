# 🚀 Quick Start Guide - Deal Verification System

## Step-by-Step Setup (5 minutes)

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Configure Environment Variables

Create a `.env` file in your project directory:

```env
# Required: Telegram API (Get from https://my.telegram.org)
TELEGRAM_API_ID=31073628
TELEGRAM_API_HASH=aa3d15671e6d93bf06ae350a77aa96bf

# Required: Supabase Database
SUPABASE_URL=https://sspufleiikzsazouzkot.supabase.co
SUPABASE_KEY=your_supabase_key_here

# Optional but Recommended: OpenAI for verification
OPENAI_API_KEY=sk-your-openai-key-here

# Verification Settings
ENABLE_DEAL_VERIFICATION=true
VERIFICATION_MIN_CONFIDENCE=0.6
```

### 3️⃣ Update Database Schema

1. Go to your Supabase project: https://supabase.com/dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `database_migration.sql`
4. Click "Run" to execute

This adds new columns for deal verification.

### 4️⃣ Run the System

```bash
python telegram_listener.py
```

You should see:
```
✅ Telegram Listener initialized
✅ Deal verification pipeline initialized
🔌 Connecting to Telegram...
✅ Successfully logged in as: Your Name
👂 Listening to 30+ channels...
```

## 🎯 What Happens Now?

### Without Verification (Legacy Mode)
```
Telegram Message → NLP Parser → Save to Database
```

### With Verification (New Mode) ✨
```
Telegram Message → NLP Parser → Verify from Official Site → 
Calculate Confidence → Save Only High-Quality Deals
```

## 📊 View Results

### Option 1: View in Terminal
```bash
python view_deals.py
```

### Option 2: Query Supabase Directly
```sql
-- View all verified deals
SELECT * FROM verified_deals LIMIT 20;

-- View high-confidence deals
SELECT * FROM high_confidence_deals LIMIT 20;
```

## 🧪 Test Individual Components

### Test URL Expansion
```bash
python url_expander.py
```

### Test Web Scraper
```bash
python product_scraper.py
```

### Test LLM Verification
```bash
python llm_verifier.py
```

### Test Full Pipeline
```bash
python deal_verification_pipeline.py
```

## ⚙️ Configuration Options

### Disable Verification (Run in Legacy Mode)
```env
ENABLE_DEAL_VERIFICATION=false
```

### Adjust Confidence Threshold
```env
# Higher = Stricter (fewer deals, higher quality)
# Lower = Lenient (more deals, may include false positives)
VERIFICATION_MIN_CONFIDENCE=0.75  # Default: 0.6
```

### Enable Debug Logging
In `telegram_listener.py`:
```python
ENABLE_DEBUG_LOGGING = True
```

## 🔍 Understanding Confidence Scores

| Score | Label | Meaning |
|-------|-------|---------|
| 0.9-1.0 | Very High | Perfect match, complete data |
| 0.75-0.89 | High | Strong match, minor discrepancies |
| 0.6-0.74 | Medium | Acceptable match, some missing data |
| 0.4-0.59 | Low | Weak match, significant issues |
| 0.0-0.39 | Very Low | Poor match, rejected |

**Only deals with score ≥ 0.6 are saved by default.**

## 🎨 Example Output

```
================================================================================
📨 New message from: TrickXpert
🤖 Parsing message with NLP...
📊 PARSED DATA:
  title             : Samsung Galaxy S23 5G
  store             : Amazon
  discount_price    : 49999
  link              : https://amzn.to/xyz123

🔍 Verifying deal from official source...
================================================================================
🔍 VERIFYING DEAL: Samsung Galaxy S23 5G
================================================================================

📎 Step 1: Expanding URL...
   ✅ Expanded to: https://www.amazon.in/dp/B0ABCD1234

🌐 Step 2: Scraping official product page...
   ✅ Successfully scraped product data
      Title: Samsung Galaxy S23 5G (Phantom Black, 128GB)
      Price: ₹49990
      MRP: ₹74999

🤖 Step 3: LLM Verification...
   ✅ Verification complete
      Verified: True
      Price Match: True
      Recommendation: ACCEPT

📊 Step 4: Calculating confidence score...
   ✅ Confidence Score: 0.92 (Very High)

================================================================================
📋 FINAL VERDICT
================================================================================
   Verified: ✅ YES
   Confidence: Very High (0.92)
   Recommendation: ACCEPT
   Issues: None
================================================================================

✅ Deal verified (confidence: 0.92)
💾 Saved to database (Total saved: 1)
```

## 🆘 Common Issues

### Issue: "OpenAI API not available"
**Solution**: Set `OPENAI_API_KEY` in `.env` or disable verification

### Issue: "Scraping failed"
**Possible causes**:
- Site blocked the request (try again later)
- URL is invalid
- Site structure changed

### Issue: "Database save error"
**Solution**: Check Supabase credentials and run migration script

### Issue: Low confidence scores
**This is normal!** Many Telegram deals are:
- Outdated
- Fake/misleading
- Priced incorrectly

The system is working correctly by filtering these out.

## 📈 Best Practices

### 1. Monitor the System
- Check logs regularly
- Review rejected deals occasionally
- Adjust confidence threshold if needed

### 2. Database Maintenance
Run cleanup weekly:
```sql
SELECT cleanup_low_confidence_deals(7);
```

### 3. API Usage
- OpenAI API costs money (but minimal for this use case)
- ~$0.01 per verification
- Monitor usage at: https://platform.openai.com/usage

### 4. Add More Sites
Extend `product_scraper.py` to support more e-commerce platforms.

## 🎯 Next Steps

1. ✅ Set up environment variables
2. ✅ Run database migration
3. ✅ Start telegram_listener.py
4. ✅ Monitor for 1 hour
5. ✅ Check results in Supabase
6. ✅ Adjust confidence threshold if needed
7. ✅ Customize for your use case

## 💡 Pro Tips

- Start with `VERIFICATION_MIN_CONFIDENCE=0.6` and adjust based on results
- Use `ENABLE_DEBUG_LOGGING=True` to understand what's happening
- Test with a single channel first before adding all channels
- Review both accepted and rejected deals to tune the system
- Consider running 24/7 on a server for continuous monitoring

---

**Need help?** Check `VERIFICATION_README.md` for detailed documentation.
