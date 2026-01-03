# Daily Deals Scraper - System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DAILY DEALS SCRAPER SYSTEM                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          CLI INTERFACE                              │
│                     (daily_deals_main.py)                           │
├─────────────────────────────────────────────────────────────────────┤
│  Commands:                                                          │
│    --run-once      → Run all scrapers immediately                   │
│    --scraper <name> → Run specific scraper                          │
│    --schedule      → Start daily scheduled jobs                     │
│    --stats         → Show database statistics                       │
│    --test-db       → Test database connection                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         SCHEDULER LAYER                             │
│                   (scheduler/daily_deals_job.py)                    │
├─────────────────────────────────────────────────────────────────────┤
│  • APScheduler (cron jobs)                                          │
│  • Job orchestration                                                │
│  • Run at 9:00 AM IST daily                                         │
│  • Logging & monitoring                                             │
│  • Summary reports                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        SCRAPER LAYER                                │
│                      (scrapers/*.py)                                │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────┤
│   Amazon     │  Flipkart    │   Myntra     │    Ajio      │  Meesho │
│   Tata Cliq  │  Reliance    │              │              │         │
├──────────────┴──────────────┴──────────────┴──────────────┴─────────┤
│  Each scraper:                                                      │
│    1. Fetches webpage (requests + BeautifulSoup)                    │
│    2. Parses HTML (CSS selectors)                                   │
│    3. Extracts deal data                                            │
│    4. Formats & validates data                                      │
│    5. Returns list of deals                                         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
         ┌──────────────────────────────────────────────┐
         │         UTILITIES LAYER                      │
         │          (utils/helpers.py)                  │
         ├──────────────────────────────────────────────┤
         │  • User-agent rotation                       │
         │  • HTTP session management                   │
         │  • Retry logic                               │
         │  • Rate limiting                             │
         │  • Price extraction                          │
         │  • Text cleaning                             │
         │  • URL validation                            │
         │  • Data formatting                           │
         └──────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                               │
│                   (database/supabase_client.py)                     │
├─────────────────────────────────────────────────────────────────────┤
│  DailyDealsDB Class:                                                │
│    • upsert_deal()         → Insert or update single deal           │
│    • upsert_deals_bulk()   → Bulk upsert operations                 │
│    • get_existing_deals()  → Retrieve deals                         │
│    • get_deal_by_url()     → Check existence                        │
│    • get_statistics()      → Get stats                              │
│    • delete_old_deals()    → Cleanup                                │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                           SUPABASE                                  │
│                      (PostgreSQL Database)                          │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────┤
│ amazon_deals │flipkart_deals│ myntra_deals │  ajio_deals  │meesho_  │
│tata_cliq_    │reliance_     │              │              │ deals   │
│deals         │digital_deals │              │              │         │
├──────────────┴──────────────┴──────────────┴──────────────┴─────────┤
│  Table Schema (all tables):                                         │
│    • id (PRIMARY KEY)                                               │
│    • product_name                                                   │
│    • category                                                       │
│    • brand                                                          │
│    • original_price                                                 │
│    • discounted_price                                               │
│    • discount_percentage                                            │
│    • product_url (UNIQUE)  ← Used for upsert                        │
│    • image_url                                                      │
│    • website_name                                                   │
│    • deal_type                                                      │
│    • collected_at                                                   │
│    • updated_at                                                     │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                          DATA FLOW DIAGRAM
═══════════════════════════════════════════════════════════════════════

1. SCRAPING FLOW:
   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ Scheduler│ -> │ Scraper  │ -> │ Website  │ -> │  Parse   │
   │  Starts  │    │  Called  │    │ Fetched  │    │   HTML   │
   └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                           │
                                                           ↓
   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ Database │ <- │  Format  │ <- │ Validate │ <- │ Extract  │
   │  Upsert  │    │   Data   │    │   Data   │    │  Data    │
   └──────────┘    └──────────┘    └──────────┘    └──────────┘

2. UPSERT LOGIC:
   ┌────────────────────────────────────────────────────┐
   │  Check if product_url exists in database?          │
   └────────────┬───────────────────────┬────────────────┘
                │ YES                   │ NO
                ↓                       ↓
   ┌────────────────────┐    ┌──────────────────────┐
   │  UPDATE existing   │    │  INSERT new record   │
   │  - prices          │    │  - all fields        │
   │  - discount %      │    │                      │
   │  - updated_at      │    │                      │
   └────────────────────┘    └──────────────────────┘

3. ANTI-BLOCKING FLOW:
   ┌────────────┐
   │   Request  │
   └─────┬──────┘
         │
   ┌─────▼───────────────────────┐
   │ 1. Random User-Agent        │
   └─────┬───────────────────────┘
         │
   ┌─────▼───────────────────────┐
   │ 2. Random Delay (1-3s)      │
   └─────┬───────────────────────┘
         │
   ┌─────▼───────────────────────┐
   │ 3. Send Request             │
   └─────┬───────────────────────┘
         │
   ┌─────▼───────────────────────┐
   │ 4. Success? ─── NO → Retry  │
   │         └─── YES → Parse    │
   └─────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                     INTEGRATION WITH EXISTING PROJECT
═══════════════════════════════════════════════════════════════════════

┌────────────────────────────────────────────────────────────────────┐
│                    EXISTING TELEGRAM LISTENER                      │
│                    (telegram_listener.py)                          │
├────────────────────────────────────────────────────────────────────┤
│  • Monitors 32+ Telegram channels                                  │
│  • Stores in 'deals' table                                         │
│  • Independent process                                             │
└────────────────────────────────────────────────────────────────────┘
                              │
                              │ NO CONFLICTS
                              │
┌────────────────────────────────────────────────────────────────────┐
│                   NEW DAILY DEALS SCRAPER                          │
│                   (daily_deals_main.py)                            │
├────────────────────────────────────────────────────────────────────┤
│  • Scrapes 7 e-commerce websites                                   │
│  • Stores in separate tables (amazon_deals, etc.)                  │
│  • Independent process                                             │
└────────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│                      SHARED SUPABASE                               │
├────────────────────────────────────────────────────────────────────┤
│  Telegram Tables:          │  E-commerce Tables:                   │
│    • deals                 │    • amazon_deals                     │
│    • channels              │    • flipkart_deals                   │
│    • ... (existing)        │    • myntra_deals                     │
│                            │    • ... (7 total)                    │
└────────────────────────────────────────────────────────────────────┘

OPTIONAL UNIFIED VIEW:
┌────────────────────────────────────────────────────────────────────┐
│  CREATE VIEW all_deals AS                                          │
│    SELECT 'Telegram' as source, * FROM deals                       │
│    UNION ALL                                                       │
│    SELECT 'Amazon' as source, * FROM amazon_deals                  │
│    UNION ALL                                                       │
│    ... (combine all sources)                                       │
└────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                         DEPLOYMENT OPTIONS
═══════════════════════════════════════════════════════════════════════

OPTION 1: Local Machine
┌──────────────────────────────────────────┐
│  Terminal 1: Telegram Listener           │
│    python telegram_listener.py           │
├──────────────────────────────────────────┤
│  Terminal 2: Daily Deals Scraper         │
│    python daily_deals_main.py --schedule │
└──────────────────────────────────────────┘

OPTION 2: Separate Processes
┌──────────────────────────────────────────┐
│  Process 1: telegram_listener.py         │
│  Process 2: daily_deals_main.py          │
│  Both run as background services         │
└──────────────────────────────────────────┘

OPTION 3: Containerized
┌──────────────────────────────────────────┐
│  Container 1: Telegram Listener          │
│  Container 2: Daily Deals Scraper        │
│  Shared: Supabase connection             │
└──────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                           ERROR HANDLING
═══════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────┐
│                      MULTI-LAYER PROTECTION                       │
├──────────────────────────────────────────────────────────────────┤
│  Layer 1: Network Level                                           │
│    • Connection timeouts                                          │
│    • Retry with exponential backoff                               │
│    • Session management                                           │
├──────────────────────────────────────────────────────────────────┤
│  Layer 2: Parsing Level                                           │
│    • Try/except blocks                                            │
│    • Graceful degradation                                         │
│    • Null checks                                                  │
├──────────────────────────────────────────────────────────────────┤
│  Layer 3: Data Level                                              │
│    • Data validation                                              │
│    • Format normalization                                         │
│    • Type checking                                                │
├──────────────────────────────────────────────────────────────────┤
│  Layer 4: Database Level                                          │
│    • Upsert conflicts handled                                     │
│    • Transaction management                                       │
│    • Constraint checks                                            │
├──────────────────────────────────────────────────────────────────┤
│  Layer 5: Application Level                                       │
│    • Comprehensive logging                                        │
│    • Job status tracking                                          │
│    • Summary reports                                              │
└──────────────────────────────────────────────────────────────────┘
```
