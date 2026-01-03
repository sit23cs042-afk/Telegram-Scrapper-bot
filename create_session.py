"""
Simple script to create and authenticate a Telegram session
"""
import asyncio
import os
from telethon import TelegramClient

# Telegram API credentials
API_ID = os.getenv('TELEGRAM_API_ID', '31073628')
API_HASH = os.getenv('TELEGRAM_API_HASH', 'aa3d15671e6d93bf06ae350a77aa96bf')
SESSION_NAME = 'discount_bot_session'

async def main():
    print("=" * 80)
    print("TELEGRAM SESSION CREATOR")
    print("=" * 80)
    print()
    print("📱 IMPORTANT: Enter your phone number with country code")
    print("   Example for India: +919876543210")
    print("   Example for US: +11234567890")
    print()
    
    # Create client
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    print("🔌 Connecting to Telegram...")
    print("📨 You will receive a code in your Telegram app")
    print()
    
    await client.start()
    
    # Get user info
    me = await client.get_me()
    print()
    print("✅ Authentication successful!")
    print(f"✅ Logged in as: {me.first_name} (@{me.username or 'no_username'})")
    print(f"✅ Phone: {me.phone or 'N/A'}")
    print()
    print(f"✅ Session file created: {SESSION_NAME}.session")
    print()
    print("=" * 80)
    print("You can now upload this session file to Render!")
    print("=" * 80)
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
