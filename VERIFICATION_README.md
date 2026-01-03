# 🚀 AI-Based Telegram Discount Verification System

A production-grade deal verification pipeline that automatically verifies discount deals from Telegram channels by scraping official e-commerce websites, using LLM-based reasoning to detect fake deals, and assigning confidence scores.

## ✨ Features

### 🎯 Core Capabilities
- **Automated Deal Verification**: Scrapes official e-commerce sites to verify claimed prices
- **LLM-Powered Reasoning**: Uses GPT-4 to analyze and validate deals intelligently
- **Multi-Site Support**: Extensible parsers for Amazon, Flipkart, Myntra, Ajio, and more
- **URL Expansion**: Automatically resolves shortened URLs (amzn.to, fkrt.it, etc.)
- **Confidence Scoring**: Assigns 0-1 confidence scores based on multiple verification factors
- **Vision AI Fallback**: OCR and vision-based extraction for image-only deals
- **Database Integration**: Stores only verified deals in Supabase with metadata

### 🛡️ Verification Pipeline
1. **URL Expansion**: Expands shortened links to real product URLs
2. **Web Scraping**: Fetches official product page using site-specific parsers
3. **LLM Verification**: Compares Telegram claim vs official data
4. **Confidence Scoring**: Calculates reliability score (price match, completeness, source)
5. **Database Storage**: Saves only high-confidence verified deals

## 📁 Project Structure

```
.
├── telegram_listener.py           # Main Telegram listener with verification
├── nlp_discount_parser.py         # NLP module for extracting deal data
├── deal_verification_pipeline.py  # Main verification orchestrator
├── url_expander.py                # URL expansion module
├── product_scraper.py             # Site-specific web scrapers
├── llm_verifier.py                # LLM-based deal verification
├── vision_extractor.py            # OCR & vision AI fallback
├── supabase_database.py           # Database interface
├── database_migration.sql         # SQL schema for verified deals
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🔧 Installation

### 1. Clone or Download Project
```bash
cd "C:\Users\yuvanshankar\Downloads\New folder (2)"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file:

```env
# Telegram API Credentials (Get from https://my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# OpenAI API (for LLM verification and vision AI)
OPENAI_API_KEY=your_openai_api_key

# Verification Settings
ENABLE_DEAL_VERIFICATION=true
VERIFICATION_MIN_CONFIDENCE=0.6
```

### 4. Run Database Migration

Run the SQL commands in `database_migration.sql` in your Supabase SQL editor to add verification columns.

## 🚀 Usage

### Basic Usage (With Verification)

```bash
python telegram_listener.py
```

This will:
1. Listen to Telegram channels for discount deals
2. Extract product information using NLP
3. Verify deals by scraping official websites
4. Save only verified high-confidence deals to database

### Disable Verification (Legacy Mode)

```bash
# In .env file
ENABLE_DEAL_VERIFICATION=false
```

### Test Individual Modules

#### Test URL Expander
```bash
python url_expander.py
```

#### Test Product Scraper
```bash
python product_scraper.py
```

#### Test LLM Verifier
```bash
python llm_verifier.py
```

#### Test Verification Pipeline
```bash
python deal_verification_pipeline.py
```

## 📊 Database Schema

### New Verification Columns

| Column | Type | Description |
|--------|------|-------------|
| `is_verified` | BOOLEAN | Whether deal was verified from official source |
| `verified_price` | NUMERIC | Actual price from official site |
| `verified_mrp` | NUMERIC | Actual MRP from official site |
| `verified_discount` | NUMERIC | Calculated discount percentage |
| `confidence_score` | NUMERIC | Confidence score (0-1) |
| `verification_source` | VARCHAR | Source: official_site, vision_extraction, telegram_text |
| `availability` | VARCHAR | Product availability status |
| `rating` | NUMERIC | Product rating from official site |
| `seller` | VARCHAR | Seller name |

### Query Examples

```sql
-- Get all verified deals
SELECT * FROM verified_deals LIMIT 10;

-- Get high-confidence deals
SELECT * FROM high_confidence_deals LIMIT 10;

-- Get deals with verification details
SELECT 
    title,
    store,
    discount_price as claimed_price,
    verified_price,
    confidence_score,
    verification_source
FROM deals
WHERE confidence_score >= 0.75
ORDER BY confidence_score DESC;

-- Clean up low-confidence deals
SELECT cleanup_low_confidence_deals(7);
```

## 🎯 How It Works

### 1. Telegram Message Processing
```
Telegram Channel → NLP Parser → Extract: Title, Price, Store, Link
```

### 2. Deal Verification Workflow
```
Shortened URL → Expand → Official Product Page
                              ↓
                         Web Scraper
                              ↓
                    Extract: Price, MRP, Title
                              ↓
                         LLM Verifier
                              ↓
                    Compare & Validate
                              ↓
                    Confidence Scoring
                              ↓
                  Save if Score >= 0.6
```

### 3. Confidence Score Calculation

Factors:
- **Price Match (40%)**: How close Telegram price is to official price
- **Data Completeness (25%)**: Availability of title, price, MRP, etc.
- **Title Match (15%)**: Product title similarity
- **Source Reliability (10%)**: official_site > vision > telegram
- **No Critical Issues (10%)**: Stock, errors, mismatches

## 🔐 Security & Best Practices

### Rate Limiting
- Built-in exponential backoff for failed requests
- Respects site rate limits
- Session management for efficient scraping

### Privacy
- Only scrapes publicly accessible pages
- No login or authentication required
- User-Agent headers to identify bot

### Data Quality
- Validates price ranges (₹10 - ₹500,000)
- Filters generic titles
- Checks for valid product links
- Removes duplicates

## 🎨 Customization

### Add New E-Commerce Sites

Create a new scraper in `product_scraper.py`:

```python
class NewSiteScraper(BaseProductScraper):
    def can_handle(self, url: str) -> bool:
        return 'newsite.com' in url.lower()
    
    def scrape(self, url: str) -> Dict:
        # Implement scraping logic
        pass
```

Register in factory:
```python
def __init__(self):
    self.scrapers = [
        AmazonScraper(),
        FlipkartScraper(),
        NewSiteScraper(),  # Add here
    ]
```

### Adjust Confidence Threshold

```python
# In .env
VERIFICATION_MIN_CONFIDENCE=0.75  # Higher = stricter
```

### Customize Verification Logic

Modify `ConfidenceScorer.calculate_confidence()` in `deal_verification_pipeline.py` to adjust weights and factors.

## 📈 Monitoring & Statistics

### View Live Statistics

```bash
python view_deals.py
```

Shows:
- Total deals
- Verified vs unverified
- Average confidence
- Deals by store/category
- Recent deals

### Database Functions

```sql
-- Get statistics
SELECT * FROM get_deal_statistics();

-- Clean up old low-confidence deals (older than 7 days)
SELECT cleanup_low_confidence_deals(7);
```

## 🐛 Troubleshooting

### Issue: Verification not working
- Check `OPENAI_API_KEY` is set correctly
- Ensure `ENABLE_DEAL_VERIFICATION=true`
- Verify internet connectivity

### Issue: Scraping fails
- Some sites may block bots (use proxies if needed)
- Check if site structure changed (update selectors)
- Enable debug logging: `ENABLE_DEBUG_LOGGING=True`

### Issue: Low confidence scores
- Telegram data may be inaccurate
- Product page may have changed
- Adjust confidence weights in pipeline

## 🔮 Future Enhancements

- [ ] Proxy rotation for large-scale scraping
- [ ] Selenium/Playwright for JavaScript-heavy sites
- [ ] Multi-language support
- [ ] Price tracking and alerts
- [ ] Browser extension for manual verification
- [ ] API endpoint for third-party integrations

## 📝 License

This project is for educational and personal use. Ensure compliance with:
- Telegram Terms of Service
- E-commerce site robots.txt and Terms of Service
- OpenAI API usage policies

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional site scrapers
- Better LLM prompts
- Performance optimizations
- Error handling
- Documentation

## 📧 Support

For issues or questions, please refer to the code comments and documentation within each module.

---

**Built with ❤️ for better deal discovery**
