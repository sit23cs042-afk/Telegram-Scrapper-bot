"""
Telegram Listener Module
========================
Listens to e-commerce discount channels on Telegram using Telethon (MTProto),
extracts structured data using NLP, and saves to database.

Author: AI Assistant
Date: December 2025
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Optional

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import User

# Import NLP parser
from nlp_discount_parser import parse_discount_message

# Import database functions (Supabase)
try:
    from supabase_database import save_to_database, init_database
except ImportError:
    print("⚠️  Warning: supabase_database.py not found. Database saving will be disabled.")
    save_to_database = None
    init_database = None

# Import image storage
try:
    from image_storage import init_storage
    IMAGE_STORAGE_ENABLED = True
except ImportError:
    print("⚠️  Warning: image_storage.py not found. Image storage will be disabled.")
    IMAGE_STORAGE_ENABLED = False
    init_storage = None

# Import deal verification pipeline
try:
    from deal_verification_pipeline import DealVerificationPipeline
    VERIFICATION_ENABLED = True
except ImportError:
    print("⚠️  Warning: deal_verification_pipeline.py not found. Verification will be disabled.")
    VERIFICATION_ENABLED = False

# Import smart categorizer
try:
    from smart_categorizer import SmartProductCategorizer
    SMART_CATEGORIZER_ENABLED = True
except ImportError:
    print("⚠️  Warning: smart_categorizer.py not found. Smart categorization will be disabled.")
    SMART_CATEGORIZER_ENABLED = False


# ============================================================================
# CONFIGURATION
# ============================================================================

# Telegram API credentials (Get from https://my.telegram.org)
API_ID = os.getenv('TELEGRAM_API_ID', '31073628')  # Your API_ID
API_HASH = os.getenv('TELEGRAM_API_HASH', 'aa3d15671e6d93bf06ae350a77aa96bf')  # Your API_HASH
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Bot token from @BotFather
PHONE_NUMBER = os.getenv('TELEGRAM_PHONE')  # Phone number for authentication (alternative to bot token)

# Session file name (stores authentication)
SESSION_NAME = 'discount_bot_session'

# Target channels to monitor (username or ID)
TARGET_CHANNELS = [
    # Original channels
    'TrickXpert',
    
    # All offer/deal channels with public usernames
    'Alibaba_loots_dealsx',
    'bestlootdealsoffers2',
    'quality_loots',
    'icoolzTrickso_Official',
    'dealblastloot',
    'dealblast',
    'dealblastshop',
    'dealblastshopping',
    'dealblast_india_free_stuff',
    'DEALBLASTER8',
    'DealLoot99',
    'dealspointricks',
    'dealspoint',
    'dealsvelocity001',
    'DealTrigger',
    'realearnkaro100',
    'realearnkaro',
    'indiafreestuffin',
    'indiafreestffin',
    'KT_DEALS',
    'bestlootdeals07',
    'lootdealsapp1143',
    'lootdealsapp',
    'lootdealsapplication',
    'bestlootdeals',
    'Offerzone_Tricks_1',
    'Online_Loot_DealsX',
    'Deals_Sale_Live',
    'yashhotdealstore',
    'powerloot',
    'trickxperto',
    'tech24deals',
    'tech24deals9',
    'tech24deals_tech_24_deals',
    'Loot_DealsX',
    'Magixdeals_Tricks',
]

# Logging configuration
ENABLE_DEBUG_LOGGING = True

# Verification configuration
ENABLE_DEAL_VERIFICATION = os.getenv('ENABLE_DEAL_VERIFICATION', 'true').lower() == 'true'
VERIFICATION_MIN_CONFIDENCE = float(os.getenv('VERIFICATION_MIN_CONFIDENCE', '0.4'))

# Smart Categorization configuration
USE_SMART_CATEGORIZATION = os.getenv('USE_SMART_CATEGORIZATION', 'true').lower() == 'true'
USE_LLM_CATEGORIZATION = os.getenv('USE_LLM_CATEGORIZATION', 'false').lower() == 'true'

# Smart Categorization configuration
USE_SMART_CATEGORIZATION = os.getenv('USE_SMART_CATEGORIZATION', 'true').lower() == 'true'
USE_LLM_CATEGORIZATION = os.getenv('USE_LLM_CATEGORIZATION', 'false').lower() == 'true'


# ============================================================================
# TELEGRAM CLIENT SETUP
# ============================================================================

class DiscountChannelListener:
    """
    Main class for listening to Telegram discount channels.
    """
    
    def __init__(self, api_id: str, api_hash: str, session_name: str, channels: list):
        """
        Initialize the Telegram listener.
        
        Args:
            api_id (str): Telegram API ID
            api_hash (str): Telegram API hash
            session_name (str): Session file name
            channels (list): List of channel usernames/IDs to monitor
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.target_channels = channels
        
        # Proxy configuration (optional)
        proxy = None
        proxy_type = os.getenv('PROXY_TYPE')  # 'socks5' or 'http'
        proxy_host = os.getenv('PROXY_HOST')
        proxy_port = os.getenv('PROXY_PORT')
        
        if proxy_type and proxy_host and proxy_port:
            if proxy_type.lower() == 'socks5':
                import socks
                proxy = (socks.SOCKS5, proxy_host, int(proxy_port))
            elif proxy_type.lower() == 'http':
                proxy = (proxy_host, int(proxy_port))
            self._log(f"🌐 Using proxy: {proxy_type}://{proxy_host}:{proxy_port}", "INFO")
        
        # Initialize Telethon client with increased timeout
        self.client = TelegramClient(
            self.session_name,
            self.api_id,
            self.api_hash,
            proxy=proxy,
            connection_retries=10,
            retry_delay=5,
            timeout=30,
            system_version="4.16.30-vxCUSTOM"
        )
        
        # Statistics
        self.messages_processed = 0
        self.messages_saved = 0
        self.messages_verified = 0
        self.errors_encountered = 0
        
        # Initialize verification pipeline if enabled
        self.verification_pipeline = None
        if ENABLE_DEAL_VERIFICATION and VERIFICATION_ENABLED:
            try:
                self.verification_pipeline = DealVerificationPipeline(
                    enable_llm=True,
                    enable_vision=True
                )
                self._log("✅ Deal verification pipeline initialized")
            except Exception as e:
                self._log(f"⚠️  Failed to initialize verification pipeline: {e}", "WARNING")
        
        # Initialize smart categorizer if enabled
        self.smart_categorizer = None
        if USE_SMART_CATEGORIZATION and SMART_CATEGORIZER_ENABLED:
            try:
                self.smart_categorizer = SmartProductCategorizer(
                    use_llm=USE_LLM_CATEGORIZATION,
                    openai_api_key=os.getenv('OPENAI_API_KEY')
                )
                method = "LLM-powered" if USE_LLM_CATEGORIZATION else "keyword-based"
                self._log(f"✅ Smart categorizer initialized ({method})")
            except Exception as e:
                self._log(f"⚠️  Failed to initialize smart categorizer: {e}", "WARNING")
        
        self._log("✅ Telegram Listener initialized")
    
    def _log(self, message: str, level: str = "INFO"):
        """
        Log a message with timestamp.
        
        Args:
            message (str): Message to log
            level (str): Log level (INFO, ERROR, WARNING, DEBUG)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    async def start(self):
        """
        Start the Telegram client and authenticate if needed.
        """
        self._log("🔌 Connecting to Telegram...")
        
        try:
            # Start with bot token if provided (best for servers)
            if BOT_TOKEN:
                self._log("🤖 Authenticating as bot...")
                await self.client.start(bot_token=BOT_TOKEN)
                me = await self.client.get_me()
                self._log(f"✅ Successfully logged in as bot: @{me.username}")
            # Otherwise use phone number if provided
            elif PHONE_NUMBER:
                self._log(f"📱 Authenticating with phone: {PHONE_NUMBER}")
                await self.client.start(phone=PHONE_NUMBER)
                me = await self.client.get_me()
                if isinstance(me, User):
                    self._log(f"✅ Successfully logged in as: {me.first_name} (@{me.username or 'no_username'})")
                    self._log(f"📱 Phone: {me.phone or 'N/A'}")
            else:
                # Interactive authentication (won't work on servers)
                await self.client.start()
                me = await self.client.get_me()
                if isinstance(me, User):
                    self._log(f"✅ Successfully logged in as: {me.first_name} (@{me.username or 'no_username'})")
                    self._log(f"📱 Phone: {me.phone or 'N/A'}")
            
            # Verify channels
            await self._verify_channels()
            
            # Register event handler
            self.client.add_event_handler(
                self.handle_new_message,
                events.NewMessage(chats=self.target_channels)
            )
            
            self._log(f"👂 Listening to {len(self.target_channels)} channels...")
            self._log("=" * 80)
            
        except Exception as e:
            self._log(f"❌ Failed to start client: {e}", "ERROR")
            raise
    
    async def _verify_channels(self):
        """
        Verify that target channels are accessible.
        """
        self._log("🔍 Verifying channel access...")
        
        accessible_channels = []
        for channel in self.target_channels:
            try:
                entity = await self.client.get_entity(channel)
                accessible_channels.append(channel)
                self._log(f"  ✓ {channel} - Accessible", "DEBUG")
            except Exception as e:
                self._log(f"  ✗ {channel} - Not accessible: {e}", "WARNING")
        
        if not accessible_channels:
            self._log("⚠️  Warning: No channels are accessible. Check channel usernames.", "WARNING")
        else:
            self._log(f"✅ {len(accessible_channels)}/{len(self.target_channels)} channels accessible")
    
    async def handle_new_message(self, event):
        """
        Handle incoming messages from monitored channels.
        
        Args:
            event: Telethon NewMessage event
        """
        try:
            # Get message details
            raw_text = event.raw_text
            sender = await event.get_sender()
            chat = await event.get_chat()
            
            # Log message received
            channel_name = getattr(chat, 'username', None) or getattr(chat, 'title', 'Unknown')
            self._log(f"\n📨 New message from: {channel_name}")
            
            if ENABLE_DEBUG_LOGGING:
                self._log(f"Raw text preview: {raw_text[:100]}...", "DEBUG")
            
            # Skip empty messages
            if not raw_text or not raw_text.strip():
                self._log("⏭️  Skipped: Empty message", "DEBUG")
                return
            
            # Parse message using NLP
            self._log("🤖 Parsing message with NLP...")
            parsed_data = self._parse_message(raw_text)
            
            if parsed_data:
                self.messages_processed += 1
                
                # Add metadata
                parsed_data['channel'] = channel_name
                parsed_data['message_id'] = event.id
                parsed_data['message_date'] = event.date.isoformat() if event.date else None
                
                # Print parsed data
                self._print_parsed_data(parsed_data)
                
                # Verify deal if verification is enabled (only needs valid link, scraper will get title/price)
                if self._should_save(parsed_data):
                    if self.verification_pipeline and ENABLE_DEAL_VERIFICATION:
                        self._log("🔍 Verifying deal from official source (scraper will extract full details)...")
                        verified_data = await self._verify_deal(parsed_data)
                        
                        # Only save if verification passed
                        if self.verification_pipeline.should_save_to_database(verified_data, VERIFICATION_MIN_CONFIDENCE):
                            # Merge verified data with original parsed data
                            parsed_data.update({
                                'is_verified': verified_data.get('is_verified', False),
                                'verified_title': verified_data.get('verified_title'),
                                'verified_price': verified_data.get('verified_price'),
                                'verified_mrp': verified_data.get('verified_mrp'),
                                'verified_discount': verified_data.get('verified_discount'),
                                'confidence_score': verified_data.get('confidence_score'),
                                'verification_source': verified_data.get('verification_source'),
                                'availability': verified_data.get('availability'),
                                'rating': verified_data.get('rating'),
                                'seller': verified_data.get('seller')
                            })
                            
                            # Re-categorize using verified title (more accurate)
                            if self.smart_categorizer and verified_data.get('verified_title'):
                                category_result = self.smart_categorizer.categorize(
                                    verified_data['verified_title'],
                                    use_verified_title=True
                                )
                                if category_result['category'] != parsed_data.get('category'):
                                    old_cat = parsed_data.get('category', 'unknown')
                                    parsed_data['category'] = category_result['category']
                                    self._log(f"📂 Re-categorized from '{old_cat}' to '{category_result['category']}' ({category_result['method']})")
                            
                            # Re-categorize using verified title (more accurate)
                            if self.smart_categorizer and verified_data.get('verified_title'):
                                category_result = self.smart_categorizer.categorize(
                                    verified_data['verified_title'],
                                    use_verified_title=True
                                )
                                parsed_data['category'] = category_result['category']
                                self._log(f"📂 Re-categorized as '{category_result['category']}' using {category_result['method']} method")
                            
                            self.messages_verified += 1
                            self._log(f"✅ Deal verified (confidence: {verified_data.get('confidence_score', 0):.2f})")
                        else:
                            self._log(f"⏭️  Deal rejected by verification (low confidence or issues)")
                            return
                    else:
                        # No verification, use smart categorization on original title if available
                        if self.smart_categorizer and parsed_data.get('title'):
                            category_result = self.smart_categorizer.categorize(
                                parsed_data['title'],
                                use_verified_title=False
                            )
                            parsed_data['category'] = category_result['category']
                    
                    # Save to database
                    success = await self._save_to_database(parsed_data)
                    if success:
                        self.messages_saved += 1
                        self._log(f"💾 Saved to database (Total saved: {self.messages_saved})")
                    else:
                        self._log("⚠️  Failed to save to database", "WARNING")
                else:
                    self._log("⏭️  Skipped: Missing required fields (title or link)")
            else:
                self._log("⚠️  Failed to parse message", "WARNING")
            
            self._log("─" * 80)
            
        except Exception as e:
            self.errors_encountered += 1
            self._log(f"❌ Error handling message: {e}", "ERROR")
            if ENABLE_DEBUG_LOGGING:
                import traceback
                self._log(traceback.format_exc(), "DEBUG")
    
    def _parse_message(self, raw_text: str) -> Optional[dict]:
        """
        Parse message using NLP module.
        
        Args:
            raw_text (str): Raw message text
            
        Returns:
            dict or None: Parsed data or None if parsing failed
        """
        try:
            parsed = parse_discount_message(raw_text)
            return parsed
        except Exception as e:
            self._log(f"❌ NLP parsing error: {e}", "ERROR")
            return None
    
    def _should_save(self, parsed_data: dict) -> bool:
        """
        Check if parsed data should proceed to verification.
        
        Args:
            parsed_data (dict): Parsed message data
            
        Returns:
            bool: True if should verify, False otherwise
        """
        # Only check for valid link - the scraper will get title/price from the official page
        has_link = parsed_data.get("link") and len(parsed_data.get("link", "").strip()) > 0
        
        if not has_link:
            self._log("⏭️  Skipped: Missing product link", "DEBUG")
            return False
        
        # Check for valid link (not Telegram channel link)
        is_valid_link = not parsed_data["link"].startswith("https://t.me/")
        if not is_valid_link:
            self._log("⏭️  Skipped: Telegram channel link, not product link", "DEBUG")
            return False
        
        return True
    
    async def _verify_deal(self, parsed_data: dict) -> dict:
        """
        Verify deal using the verification pipeline.
        
        Args:
            parsed_data (dict): Parsed message data from NLP
            
        Returns:
            dict: Verification results
        """
        try:
            # Run verification in a separate thread to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            verification_result = await loop.run_in_executor(
                None,
                self.verification_pipeline.verify_deal,
                parsed_data
            )
            return verification_result
        except Exception as e:
            self._log(f"❌ Verification error: {e}", "ERROR")
            return {
                'is_verified': False,
                'confidence_score': 0.0,
                'verification_source': 'telegram_text',
                'issues': [f'Verification failed: {str(e)}']
            }
    
    async def _save_to_database(self, data: dict) -> bool:
        """
        Save parsed data to database.
        
        Args:
            data (dict): Parsed message data
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if save_to_database is None:
            self._log("⚠️  Database module not available", "WARNING")
            return False
        
        try:
            # Call database save function
            result = save_to_database(data)
            return result
        except Exception as e:
            self._log(f"❌ Database save error: {e}", "ERROR")
            return False
    
    def _print_parsed_data(self, data: dict):
        """
        Pretty print parsed data for debugging.
        
        Args:
            data (dict): Parsed message data
        """
        self._log("📊 PARSED DATA:")
        
        # Print main fields
        fields_to_print = [
            'title', 'store', 'mrp', 'discount_price',
            'discount_percent', 'link', 'category'
        ]
        
        for field in fields_to_print:
            value = data.get(field, '')
            self._log(f"  {field:18s}: {value}")
    
    def print_statistics(self):
        """
        Print session statistics.
        """
        self._log("\n" + "=" * 80)
        self._log("📊 SESSION STATISTICS")
        self._log("=" * 80)
        self._log(f"  Messages Processed : {self.messages_processed}")
        self._log(f"  Messages Saved     : {self.messages_saved}")
        self._log(f"  Errors Encountered : {self.errors_encountered}")
        self._log("=" * 80)
    
    async def run(self):
        """
        Run the listener (blocks until interrupted).
        """
        try:
            self._log("🚀 Starting listener...")
            await self.start()
            
            # Run until disconnected
            self._log("✅ Listener is now active. Press Ctrl+C to stop.")
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            self._log("\n⏹️  Stopping listener...")
        except Exception as e:
            self._log(f"❌ Fatal error: {e}", "ERROR")
            raise
        finally:
            self.print_statistics()
            await self.client.disconnect()
            self._log("👋 Disconnected from Telegram")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def main():
    """
    Main entry point for the Telegram listener.
    """
    print("\n" + "=" * 80)
    print("🤖 E-COMMERCE DISCOUNT AI AGENT - TELEGRAM LISTENER")
    print("=" * 80 + "\n")
    
    # Validate configuration
    if API_ID == '12345678' or API_HASH == 'your_api_hash_here':
        print("❌ ERROR: Please configure your API_ID and API_HASH")
        print("Get them from: https://my.telegram.org")
        print("\nSet environment variables:")
        print("  export TELEGRAM_API_ID='your_api_id'")
        print("  export TELEGRAM_API_HASH='your_api_hash'")
        print("\nOr edit the configuration in telegram_listener.py")
        sys.exit(1)
    
    # Initialize database
    if init_database:
        try:
            init_database()
            print("✅ Database initialized\n")
        except Exception as e:
            print(f"⚠️  Warning: Database initialization failed: {e}\n")
    
    # Initialize image storage
    if IMAGE_STORAGE_ENABLED and init_storage:
        try:
            init_storage()
            print("✅ Image storage initialized\n")
        except Exception as e:
            print(f"⚠️  Warning: Image storage initialization failed: {e}\n")
    
    # Create and run listener
    listener = DiscountChannelListener(
        api_id=API_ID,
        api_hash=API_HASH,
        session_name=SESSION_NAME,
        channels=TARGET_CHANNELS
    )
    
    await listener.run()


# ============================================================================
# MANUAL TESTING MODE
# ============================================================================

async def test_manual_messages():
    """
    Test the NLP parser with sample messages (without Telegram connection).
    """
    print("\n" + "=" * 80)
    print("🧪 MANUAL TESTING MODE - NLP PARSER ONLY")
    print("=" * 80 + "\n")
    
    # Sample test messages
    test_messages = [
        {
            "channel": "amazon_deals",
            "text": "🔥 Amazon Deal: Boat Airdopes 441 at ₹999 (MRP ₹2999) – 67% Off. Buy Now: https://amzn.to/xxxx"
        },
        {
            "channel": "flipkart_offers",
            "text": "Flipkart Offer!! Redmi A3 now at just Rs. 6499 (Original Price: Rs 7999). Link: https://fkrt.it/xxxxx"
        },
        {
            "channel": "myntra_sale",
            "text": "🛍️ MYNTRA SALE: Nike Air Max Shoes - Was Rs.8999, Now Only Rs.4499 (50% OFF) https://myntra.com/deal123"
        }
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST MESSAGE {i} - Channel: {msg['channel']}")
        print(f"{'─' * 80}")
        print(f"Raw text: {msg['text']}")
        print()
        
        # Parse message
        try:
            parsed = parse_discount_message(msg['text'])
            
            # Add metadata
            parsed['channel'] = msg['channel']
            
            # Print results
            print("📊 PARSED OUTPUT:")
            for key, value in parsed.items():
                if key != 'timestamp':
                    print(f"  {key:18s}: {value}")
            
            # Check if should save
            should_save = parsed.get('title') and parsed.get('link')
            print(f"\n💾 Would save to database: {'YES ✅' if should_save else 'NO ❌'}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Manual testing completed")
    print("=" * 80 + "\n")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Telegram Discount Channel Listener')
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in manual testing mode (no Telegram connection)'
    )
    args = parser.parse_args()
    
    # Run in appropriate mode
    if args.test:
        # Manual testing mode
        asyncio.run(test_manual_messages())
    else:
        # Normal mode - connect to Telegram
        asyncio.run(main())
