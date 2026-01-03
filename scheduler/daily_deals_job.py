"""
Daily Deals Scheduler
Runs scrapers periodically and stores data in Supabase
"""

import logging
from datetime import datetime, time
from typing import Dict
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from scrapers import (
    scrape_amazon_deals,
    scrape_flipkart_deals,
    scrape_myntra_deals,
    scrape_ajio_deals,
    scrape_meesho_deals,
    scrape_tata_cliq_deals,
    scrape_reliance_digital_deals
)
from database import get_db_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyDealsScheduler:
    """Scheduler for running daily deals scrapers"""
    
    def __init__(self):
        self.db = get_db_client()
        self.scheduler = BlockingScheduler(timezone=pytz.timezone('Asia/Kolkata'))
        
        # Configuration
        self.max_deals_per_site = int(os.getenv('MAX_DEALS_PER_SITE', 50))
        
        # Scraper mapping
        self.scrapers = {
            'amazon': scrape_amazon_deals,
            'flipkart': scrape_flipkart_deals,
            'myntra': scrape_myntra_deals,
            'ajio': scrape_ajio_deals,
            'meesho': scrape_meesho_deals,
            'tata_cliq': scrape_tata_cliq_deals,
            'reliance_digital': scrape_reliance_digital_deals
        }
    
    def scrape_and_store(self, website: str, scraper_func) -> Dict:
        """
        Run a scraper and store results in database
        
        Args:
            website: Website name
            scraper_func: Scraper function to execute
            
        Returns:
            Dictionary with results
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting scraper for: {website.upper()}")
        logger.info(f"{'='*60}")
        
        try:
            # Run scraper
            deals = scraper_func(max_deals=self.max_deals_per_site)
            
            if not deals:
                logger.warning(f"No deals found for {website}")
                return {'website': website, 'success': 0, 'failed': 0, 'total': 0}
            
            # Store in database
            results = self.db.upsert_deals_bulk(website, deals)
            
            logger.info(f"✓ Completed {website}: {results['success']} deals stored")
            results['website'] = website
            results['total'] = len(deals)
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Error processing {website}: {e}")
            return {'website': website, 'success': 0, 'failed': 0, 'total': 0, 'error': str(e)}
    
    def run_all_scrapers(self):
        """Run all scrapers sequentially"""
        logger.info("\n" + "="*60)
        logger.info("🚀 DAILY DEALS SCRAPING JOB STARTED")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60 + "\n")
        
        results = []
        
        for website, scraper_func in self.scrapers.items():
            result = self.scrape_and_store(website, scraper_func)
            results.append(result)
        
        # Print summary
        self._print_summary(results)
    
    def _print_summary(self, results: list):
        """Print job summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 SCRAPING JOB SUMMARY")
        logger.info("="*60)
        
        total_success = sum(r['success'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        total_deals = sum(r['total'] for r in results)
        
        for result in results:
            website = result['website']
            success = result['success']
            failed = result['failed']
            total = result['total']
            
            status = "✓" if success > 0 else "✗"
            logger.info(f"{status} {website.upper()}: {success}/{total} deals stored")
        
        logger.info("-" * 60)
        logger.info(f"TOTAL: {total_success} deals stored successfully")
        logger.info(f"FAILED: {total_failed} deals failed to store")
        logger.info(f"SCRAPED: {total_deals} total deals")
        logger.info("="*60 + "\n")
    
    def run_single_scraper(self, website: str):
        """
        Run a single scraper
        
        Args:
            website: Website name to scrape
        """
        if website not in self.scrapers:
            logger.error(f"Unknown website: {website}")
            logger.info(f"Available websites: {', '.join(self.scrapers.keys())}")
            return
        
        scraper_func = self.scrapers[website]
        result = self.scrape_and_store(website, scraper_func)
        self._print_summary([result])
    
    def start_scheduled_jobs(self, hour: int = 9, minute: int = 0):
        """
        Start scheduled jobs
        
        Args:
            hour: Hour to run (24-hour format, default 9 AM)
            minute: Minute to run (default 0)
        """
        logger.info("⏰ Starting Daily Deals Scheduler")
        logger.info(f"Scheduled to run daily at {hour:02d}:{minute:02d} IST")
        
        # Schedule daily job
        self.scheduler.add_job(
            self.run_all_scrapers,
            CronTrigger(hour=hour, minute=minute),
            id='daily_deals_job',
            name='Daily Deals Scraping Job',
            replace_existing=True
        )
        
        logger.info("Scheduler started. Press Ctrl+C to exit.")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()


def main():
    """Main entry point for scheduler"""
    scheduler = DailyDealsScheduler()
    
    # Get schedule configuration from environment
    schedule_hour = int(os.getenv('SCHEDULE_HOUR', 9))
    schedule_minute = int(os.getenv('SCHEDULE_MINUTE', 0))
    
    # Check if running in immediate mode
    run_now = os.getenv('RUN_NOW', 'false').lower() == 'true'
    
    if run_now:
        logger.info("Running scrapers immediately (RUN_NOW=true)")
        scheduler.run_all_scrapers()
    else:
        scheduler.start_scheduled_jobs(hour=schedule_hour, minute=schedule_minute)


if __name__ == "__main__":
    main()
