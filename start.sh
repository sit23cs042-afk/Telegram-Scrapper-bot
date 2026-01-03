#!/bin/bash

# Start script for Telegram Discount Bot on Render
echo "Starting Telegram Discount Bot..."

# Check if required environment variables are set
if [ -z "$TELEGRAM_API_ID" ] || [ -z "$TELEGRAM_API_HASH" ]; then
    echo "ERROR: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set"
    exit 1
fi

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "ERROR: SUPABASE_URL and SUPABASE_KEY must be set"
    exit 1
fi

echo "Environment variables validated ✓"

# Run the Telegram listener
python telegram_listener.py
