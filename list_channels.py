"""
List All Telegram Channels
===========================
Fetches all channels from your Telegram account to select which ones to monitor.
"""

import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel

API_ID = '31073628'
API_HASH = 'aa3d15671e6d93bf06ae350a77aa96bf'
SESSION_NAME = 'discount_bot_session'

async def list_all_channels():
    """Fetch and display all channels from Telegram account"""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    await client.start()
    print(f"✅ Logged in\n")
    
    print("="*80)
    print("📺 FETCHING ALL CHANNELS FROM YOUR ACCOUNT")
    print("="*80)
    print()
    
    channels = []
    
    # Get all dialogs (chats, channels, groups)
    async for dialog in client.iter_dialogs():
        # Filter only channels
        if isinstance(dialog.entity, Channel) and dialog.entity.broadcast:
            username = dialog.entity.username or "No username"
            title = dialog.entity.title
            channels.append({
                'username': username,
                'title': title,
                'id': dialog.entity.id
            })
    
    # Sort by title
    channels.sort(key=lambda x: x['title'].lower())
    
    # Display channels
    print(f"Found {len(channels)} channels:\n")
    
    # Filter channels with "offer" or "deal" in the name
    offer_channels = [ch for ch in channels if any(word in ch['title'].lower() 
                     for word in ['offer', 'deal', 'discount', 'loot', 'bargain', 'sale'])]
    
    if offer_channels:
        print("🎯 CHANNELS WITH OFFERS/DEALS IN NAME:")
        print("-" * 80)
        for i, ch in enumerate(offer_channels, 1):
            username = f"@{ch['username']}" if ch['username'] != "No username" else "(private)"
            print(f"{i:3d}. {ch['title'][:50]:<50} | {username}")
        print()
    
    print("\n📋 ALL CHANNELS:")
    print("-" * 80)
    for i, ch in enumerate(channels, 1):
        username = f"@{ch['username']}" if ch['username'] != "No username" else "(private)"
        print(f"{i:3d}. {ch['title'][:50]:<50} | {username}")
    
    print("\n" + "="*80)
    print(f"✅ Total channels found: {len(channels)}")
    print(f"✅ Offer/Deal channels: {len(offer_channels)}")
    print("="*80)
    
    # Save to file
    with open('channels_list.txt', 'w', encoding='utf-8') as f:
        f.write("ALL TELEGRAM CHANNELS\n")
        f.write("="*80 + "\n\n")
        for ch in channels:
            username = ch['username'] if ch['username'] != "No username" else ""
            f.write(f"{ch['title']}\n")
            if username:
                f.write(f"  Username: @{username}\n")
            f.write(f"  ID: {ch['id']}\n\n")
    
    print("\n💾 Full list saved to: channels_list.txt")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(list_all_channels())
