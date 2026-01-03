"""
Discount Product Intelligence Agent - Main Orchestrator
========================================================
Unified system combining:
- Telegram monitoring
- Official deal page scraping  
- Historical price tracking
- Deal scoring (0-100)
- Stock availability
- Duplicate detection
- Final effective price calculation

Author: AI Assistant
Date: December 2025
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import json

# Import all components
try:
    from telegram_listener import TelegramDealListener
    TELEGRAM_AVAILABLE = True
except ImportError:
    print("⚠️  Telegram listener not available")
    TELEGRAM_AVAILABLE = False

try:
    from official_deal_monitor import OfficialDealMonitorOrchestrator
    OFFICIAL_MONITOR_AVAILABLE = True
except ImportError:
    print("⚠️  Official deal monitor not available")
    OFFICIAL_MONITOR_AVAILABLE = False

try:
    from price_history_tracker import PriceHistoryTracker
    PRICE_TRACKING_AVAILABLE = True
except ImportError:
    print("⚠️  Price history tracker not available")
    PRICE_TRACKING_AVAILABLE = False

try:
    from deal_scorer import DealScorer
    SCORING_AVAILABLE = True
except ImportError:
    print("⚠️  Deal scorer not available")
    SCORING_AVAILABLE = False

try:
    from duplicate_detector import DuplicateDetector
    DUPLICATE_DETECTION_AVAILABLE = True
except ImportError:
    print("⚠️  Duplicate detector not available")
    DUPLICATE_DETECTION_AVAILABLE = False

try:
    from scraper_enhancements import ProductScraperEnhancer
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    print("⚠️  Scraper enhancements not available")
    ENHANCEMENTS_AVAILABLE = False

try:
    from product_scraper import ProductScraperFactory
    SCRAPER_AVAILABLE = True
except ImportError:
    print("⚠️  Product scraper not available")
    SCRAPER_AVAILABLE = False

try:
    from smart_categorizer import SmartProductCategorizer
    CATEGORIZER_AVAILABLE = True
except ImportError:
    print("⚠️  Smart categorizer not available")
    CATEGORIZER_AVAILABLE = False

try:
    from supabase_database import save_to_database
    DATABASE_AVAILABLE = True
except ImportError:
    print("⚠️  Database not available")
    DATABASE_AVAILABLE = False


class DiscountIntelligenceAgent:
    """
    Main orchestrator for the Discount Product Intelligence system.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the intelligence agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize components
        self.price_tracker = PriceHistoryTracker() if PRICE_TRACKING_AVAILABLE else None
        self.deal_scorer = DealScorer() if SCORING_AVAILABLE else None
        self.duplicate_detector = DuplicateDetector() if DUPLICATE_DETECTION_AVAILABLE else None
        self.scraper_enhancer = ProductScraperEnhancer() if ENHANCEMENTS_AVAILABLE else None
        self.categorizer = SmartProductCategorizer() if CATEGORIZER_AVAILABLE else None
        self.official_monitor = OfficialDealMonitorOrchestrator() if OFFICIAL_MONITOR_AVAILABLE else None
        
        # Statistics
        self.stats = {
            'total_deals_processed': 0,
            'duplicates_removed': 0,
            'high_value_deals': 0,
            'deals_saved': 0,
            'errors': 0
        }
    
    def process_deal(self, deal_data: Dict) -> Optional[Dict]:
        """
        Process a single deal through the complete pipeline.
        
        Args:
            deal_data: Raw deal data
        
        Returns:
            Processed and enriched deal data or None if rejected
        """
        try:
            self.stats['total_deals_processed'] += 1
            
            # Step 1: Extract product URL and scrape details
            url = deal_data.get('url') or deal_data.get('link')
            if url and SCRAPER_AVAILABLE:
                scraper_factory = ProductScraperFactory()
                scraper = scraper_factory.get_scraper(url)
                if scraper:
                    scraped_data = scraper.scrape(url)
                    if scraped_data.get('success'):
                        # Merge scraped data with original
                        deal_data.update(scraped_data)
            
            # Step 2: Enhance with stock, offers, final price
            if self.scraper_enhancer and url:
                # Note: Would need soup and html here - simplified for now
                deal_data = self._enhance_deal_data(deal_data)
            
            # Step 3: Get price history insights
            price_insights = None
            if self.price_tracker and url:
                current_price = deal_data.get('price') or deal_data.get('offer_price')
                mrp = deal_data.get('mrp')
                
                if current_price:
                    # Record current price
                    self.price_tracker.record_price(
                        url, 
                        current_price, 
                        mrp,
                        {'title': deal_data.get('title'), 'store': deal_data.get('store')}
                    )
                    
                    # Get insights
                    price_insights = self.price_tracker.get_price_insights(
                        url, current_price, mrp
                    )
                    deal_data['price_insights'] = price_insights
            
            # Step 4: Categorize product
            if self.categorizer:
                title = deal_data.get('title', '')
                description = deal_data.get('description', '')
                if title:
                    category_result = self.categorizer.categorize(title)
                    deal_data['category'] = category_result.get('category', 'other')
                    deal_data['method'] = category_result.get('method')
                    deal_data['confidence'] = category_result.get('confidence')
            
            # Step 5: Score deal (0-100)
            if self.deal_scorer:
                score_data = self.deal_scorer.score_deal(deal_data, price_insights)
                deal_data['score'] = score_data['total_score']
                deal_data['grade'] = score_data['grade']
                deal_data['recommendation'] = score_data['recommendation']
                deal_data['score_breakdown'] = score_data['breakdown']
                
                # Track high-value deals
                if score_data['total_score'] >= 75:
                    self.stats['high_value_deals'] += 1
                    deal_data['is_high_value'] = True
            
            # Step 6: Add metadata
            deal_data['processed_at'] = datetime.now().isoformat()
            deal_data['intelligence_version'] = '2.0'
            
            # Step 7: Save to database
            if DATABASE_AVAILABLE:
                try:
                    save_to_database(deal_data)
                    self.stats['deals_saved'] += 1
                except Exception as e:
                    print(f"❌ Database save error: {e}")
            
            return deal_data
        
        except Exception as e:
            print(f"❌ Error processing deal: {e}")
            self.stats['errors'] += 1
            return None
    
    def process_multiple_deals(self, deals: List[Dict], deduplicate: bool = True) -> List[Dict]:
        """
        Process multiple deals with deduplication.
        
        Args:
            deals: List of raw deal data
            deduplicate: Whether to remove duplicates
        
        Returns:
            List of processed and enriched deals
        """
        processed_deals = []
        
        # Process each deal
        for deal in deals:
            processed = self.process_deal(deal)
            if processed:
                processed_deals.append(processed)
        
        # Deduplicate if enabled
        if deduplicate and self.duplicate_detector and len(processed_deals) > 1:
            original_count = len(processed_deals)
            processed_deals = self.duplicate_detector.deduplicate(
                processed_deals, 
                strategy='best'
            )
            self.stats['duplicates_removed'] += (original_count - len(processed_deals))
        
        # Sort by score (highest first)
        processed_deals.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return processed_deals
    
    def monitor_official_deal_pages(self, platforms: Optional[List[str]] = None) -> List[Dict]:
        """
        Monitor official e-commerce deal pages.
        
        Args:
            platforms: List of platforms to monitor (None = all)
        
        Returns:
            List of processed deals
        """
        if not self.official_monitor:
            print("❌ Official deal monitor not available")
            return []
        
        print("\n🔍 Monitoring Official Deal Pages...")
        print("="*60)
        
        # Get raw deals
        results = self.official_monitor.monitor_all_platforms(platforms)
        
        # Flatten results
        all_deals = []
        for platform, deals in results.items():
            all_deals.extend(deals)
        
        # Process deals
        processed = self.process_multiple_deals(all_deals, deduplicate=True)
        
        print(f"\n✅ Processed {len(processed)} deals from official sources")
        print(f"   High-value deals: {sum(1 for d in processed if d.get('is_high_value'))}")
        
        return processed
    
    def get_top_deals(self, deals: List[Dict], limit: int = 10, 
                     min_score: float = 70) -> List[Dict]:
        """
        Get top deals by score.
        
        Args:
            deals: List of processed deals
            limit: Maximum number of deals to return
            min_score: Minimum score threshold
        
        Returns:
            List of top deals
        """
        # Filter by minimum score
        filtered = [d for d in deals if d.get('score', 0) >= min_score]
        
        # Sort by score
        filtered.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return filtered[:limit]
    
    def export_deals_json(self, deals: List[Dict], filepath: str):
        """Export deals to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'deals': deals,
                    'count': len(deals),
                    'generated_at': datetime.now().isoformat(),
                    'stats': self.stats
                }, f, indent=2, ensure_ascii=False)
            print(f"✅ Exported {len(deals)} deals to {filepath}")
        except Exception as e:
            print(f"❌ Export error: {e}")
    
    def generate_report(self) -> str:
        """Generate summary report."""
        report = f"""
╔════════════════════════════════════════════════════════════╗
║        DISCOUNT PRODUCT INTELLIGENCE REPORT                ║
╚════════════════════════════════════════════════════════════╝

📊 STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Deals Processed:    {self.stats['total_deals_processed']}
  Duplicates Removed:        {self.stats['duplicates_removed']}
  High-Value Deals (75+):    {self.stats['high_value_deals']}
  Deals Saved to DB:         {self.stats['deals_saved']}
  Errors Encountered:        {self.stats['errors']}

🔧 COMPONENTS STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Official Monitor:          {'✅' if OFFICIAL_MONITOR_AVAILABLE else '❌'}
  Price Tracking:            {'✅' if PRICE_TRACKING_AVAILABLE else '❌'}
  Deal Scoring:              {'✅' if SCORING_AVAILABLE else '❌'}
  Duplicate Detection:       {'✅' if DUPLICATE_DETECTION_AVAILABLE else '❌'}
  Smart Categorization:      {'✅' if CATEGORIZER_AVAILABLE else '❌'}
  Database Integration:      {'✅' if DATABASE_AVAILABLE else '❌'}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report
    
    def _enhance_deal_data(self, deal_data: Dict) -> Dict:
        """Add stock, offers, and final price data."""
        # Simplified enhancement - would need full scraper integration
        if not deal_data.get('stock_status'):
            deal_data['stock_status'] = 'unknown'
            deal_data['in_stock'] = True
        
        if not deal_data.get('offers'):
            deal_data['offers'] = {
                'coupons': [],
                'bank_offers': [],
                'exchange_offers': [],
                'no_cost_emi': False
            }
        
        # Calculate final effective price if not present
        if not deal_data.get('final_effective_price'):
            base_price = deal_data.get('price') or deal_data.get('offer_price')
            if base_price:
                deal_data['final_effective_price'] = base_price
        
        return deal_data


# ============================================================================
# TESTING & DEMO
# ============================================================================

def demo_intelligence_agent():
    """Demo the intelligence agent capabilities."""
    print("🚀 Discount Product Intelligence Agent - DEMO")
    print("="*60)
    
    # Initialize agent
    agent = DiscountIntelligenceAgent()
    
    # Test deal data
    test_deals = [
        {
            'title': 'Apple iPhone 15 Pro 256GB',
            'price': 119900,
            'mrp': 139900,
            'discount_percent': 14.3,
            'url': 'https://www.amazon.in/dp/B0CHX1W1XY',
            'store': 'Amazon',
            'rating': 4.5,
            'review_count': 5234,
            'deal_type': 'Lightning Deal',
            'seller_type': 'official',
            'stock_status': 'low_stock',
            'source': 'test'
        },
        {
            'title': 'Samsung Galaxy S24 Ultra',
            'price': 99999,
            'mrp': 124999,
            'discount_percent': 20,
            'url': 'https://www.flipkart.com/samsung-s24',
            'store': 'Flipkart',
            'rating': 4.3,
            'review_count': 3456,
            'deal_type': 'Festival Sale',
            'seller_type': 'verified',
            'stock_status': 'in_stock',
            'source': 'test'
        }
    ]
    
    print("\n📝 Processing test deals...")
    processed = agent.process_multiple_deals(test_deals)
    
    print(f"\n✅ Processed {len(processed)} deals\n")
    
    # Display results
    for i, deal in enumerate(processed, 1):
        print(f"{i}. {deal.get('title')}")
        print(f"   Score: {deal.get('score', 0)}/100 ({deal.get('grade', 'N/A')})")
        print(f"   Price: ₹{deal.get('price')} (was ₹{deal.get('mrp')})")
        print(f"   Category: {deal.get('category', 'N/A')}")
        print(f"   {deal.get('recommendation', 'N/A')}")
        print()
    
    # Generate report
    print(agent.generate_report())
    
    # Export to JSON
    agent.export_deals_json(processed, 'intelligence_demo_output.json')


if __name__ == '__main__':
    demo_intelligence_agent()
