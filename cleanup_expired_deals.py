"""
Automated Deal Cleanup Script
==============================
Automatically removes expired deals from the database.

This script should be run periodically (e.g., daily via cron/Task Scheduler)
to keep the database clean and remove offers that have expired.

Usage:
    python cleanup_expired_deals.py

Schedule on Windows (Task Scheduler):
    1. Open Task Scheduler
    2. Create Basic Task
    3. Set trigger: Daily at 2:00 AM
    4. Action: Start a program
    5. Program: python
    6. Arguments: C:\\path\\to\\cleanup_expired_deals.py
    7. Start in: C:\\path\\to\\project

Schedule on Linux (cron):
    0 2 * * * cd /path/to/project && python cleanup_expired_deals.py >> cleanup.log 2>&1

Author: AI Assistant
Date: December 2025
"""

import sys
from datetime import datetime
from supabase_database import init_database, cleanup_expired_deals


def main():
    """Main cleanup function."""
    print("=" * 80)
    print("AUTOMATED DEAL CLEANUP")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    try:
        # Initialize database
        print("🔌 Connecting to database...")
        init_database()
        print("✅ Database connected")
        print()
        
        # Run cleanup
        print("🧹 Running cleanup...")
        deleted_count = cleanup_expired_deals()
        
        if deleted_count > 0:
            print(f"✅ Successfully removed {deleted_count} expired deal(s)")
        else:
            print("✅ No expired deals found - database is clean")
        
        print()
        print("=" * 80)
        print("CLEANUP COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        print()
        print("=" * 80)
        print("CLEANUP FAILED")
        print("=" * 80)
        print()
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
