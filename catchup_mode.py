"""
Run Telegram Bot in Catch-Up Mode Only
Processes missed messages and exits (no live monitoring)
Perfect for scheduled runs (cron/task scheduler)
"""
import asyncio
import os
import sys
from datetime import datetime

from telegram_listener import (
    DiscountChannelListener,
    API_ID,
    API_HASH,
    SESSION_NAME,
    TARGET_CHANNELS,
    init_database,
    IMAGE_STORAGE_ENABLED,
    init_storage
)

async def catchup_only():
    """Run catch-up mode and exit"""
    print("\n" + "=" * 80)
    print("📥 TELEGRAM BOT - CATCH-UP MODE")
    print("=" * 80 + "\n")
    
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
    
    # Create listener with catch-up enabled
    listener = DiscountChannelListener(
        api_id=API_ID,
        api_hash=API_HASH,
        session_name=SESSION_NAME,
        channels=TARGET_CHANNELS,
        catchup_mode=True
    )
    
    try:
        # Connect and authenticate
        await listener.start()
        
        # Process missed messages
        await listener.catch_up_messages()
        
        # Print statistics
        listener.print_statistics()
        
        # Disconnect
        await listener.client.disconnect()
        print("\n✅ Catch-up complete! Exiting...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set catch-up period (hours) - default 24
    # Override with environment variable: CATCHUP_HOURS=48
    catchup_hours = os.getenv('CATCHUP_HOURS', '24')
    print(f"⏰ Will catch up on last {catchup_hours} hours of messages\n")
    
    asyncio.run(catchup_only())
