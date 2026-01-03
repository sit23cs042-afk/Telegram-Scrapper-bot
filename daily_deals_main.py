"""
Daily Deals Scraper - Main Entry Point
Orchestrates the daily deals scraping system
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from scheduler import DailyDealsScheduler
from database import get_db_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_environment():
    """Verify that all required environment variables are set"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set them in your .env file or environment")
        return False
    
    logger.info("✓ Environment variables validated")
    return True


def test_database_connection():
    """Test database connection"""
    try:
        db = get_db_client()
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def run_once():
    """Run all scrapers once"""
    logger.info("Running scrapers once...")
    scheduler = DailyDealsScheduler()
    scheduler.run_all_scrapers()


def run_single(website: str):
    """Run a single scraper"""
    logger.info(f"Running scraper for {website}...")
    scheduler = DailyDealsScheduler()
    scheduler.run_single_scraper(website)


def run_scheduled():
    """Run schedulers"""
    logger.info("Starting scheduled jobs...")
    
    schedule_hour = int(os.getenv('SCHEDULE_HOUR', 9))
    schedule_minute = int(os.getenv('SCHEDULE_MINUTE', 0))
    
    scheduler = DailyDealsScheduler()
    scheduler.start_scheduled_jobs(hour=schedule_hour, minute=schedule_minute)


def show_stats():
    """Show database statistics"""
    db = get_db_client()
    websites = ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'tata_cliq', 'reliance_digital']
    
    logger.info("\n" + "="*60)
    logger.info("📊 DATABASE STATISTICS")
    logger.info("="*60)
    
    total_deals = 0
    for website in websites:
        stats = db.get_statistics(website)
        count = stats.get('total_deals', 0)
        total_deals += count
        logger.info(f"{website.upper()}: {count} deals")
    
    logger.info("-" * 60)
    logger.info(f"TOTAL DEALS: {total_deals}")
    logger.info("="*60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Daily Deals Scraper for Indian E-commerce Sites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all scrapers once
  python daily_deals_main.py --run-once
  
  # Run a single scraper
  python daily_deals_main.py --scraper flipkart
  
  # Start scheduled jobs (daily at 9 AM)
  python daily_deals_main.py --schedule
  
  # Show database statistics
  python daily_deals_main.py --stats
  
  # Test database connection
  python daily_deals_main.py --test-db
        """
    )
    
    parser.add_argument('--run-once', action='store_true',
                        help='Run all scrapers once and exit')
    parser.add_argument('--scraper', type=str,
                        choices=['amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'tata_cliq', 'reliance_digital'],
                        help='Run a specific scraper')
    parser.add_argument('--schedule', action='store_true',
                        help='Start scheduled jobs (runs daily)')
    parser.add_argument('--stats', action='store_true',
                        help='Show database statistics')
    parser.add_argument('--test-db', action='store_true',
                        help='Test database connection')
    
    args = parser.parse_args()
    
    # Verify environment
    if not verify_environment():
        sys.exit(1)
    
    # Handle commands
    if args.test_db:
        test_database_connection()
    
    elif args.stats:
        if not test_database_connection():
            sys.exit(1)
        show_stats()
    
    elif args.run_once:
        if not test_database_connection():
            sys.exit(1)
        run_once()
    
    elif args.scraper:
        if not test_database_connection():
            sys.exit(1)
        run_single(args.scraper)
    
    elif args.schedule:
        if not test_database_connection():
            sys.exit(1)
        run_scheduled()
    
    else:
        parser.print_help()
        logger.info("\nNo command specified. Use --help for usage information.")


if __name__ == "__main__":
    main()
