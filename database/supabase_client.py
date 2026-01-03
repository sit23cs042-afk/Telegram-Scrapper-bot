"""
Supabase Client for Daily Deals Management
Handles database operations for e-commerce deals with upsert logic
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyDealsDB:
    """Database client for managing daily deals across multiple e-commerce platforms"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Table mapping for each website
        self.table_map = {
            'amazon': 'amazon_deals',
            'flipkart': 'flipkart_deals',
            'myntra': 'myntra_deals',
            'ajio': 'ajio_deals',
            'meesho': 'meesho_deals',
            'tata_cliq': 'tata_cliq_deals',
            'reliance_digital': 'reliance_digital_deals'
        }
    
    def _get_table_name(self, website: str) -> str:
        """Get table name for a website"""
        website = website.lower().replace(' ', '_')
        return self.table_map.get(website, f"{website}_deals")
    
    def upsert_deal(self, website: str, deal: Dict) -> bool:
        """
        Insert or update a deal based on product_url
        
        Args:
            website: Name of the e-commerce website
            deal: Dictionary containing deal information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            table_name = self._get_table_name(website)
            
            # Prepare deal data
            deal_data = {
                'product_name': deal.get('product_name'),
                'category': deal.get('category'),
                'brand': deal.get('brand'),
                'original_price': deal.get('original_price'),
                'discounted_price': deal.get('discounted_price'),
                'discount_percentage': deal.get('discount_percentage'),
                'product_url': deal.get('product_url'),
                'image_url': deal.get('image_url'),
                'website_name': website,
                'deal_type': deal.get('deal_type', 'Daily Deal'),
                'collected_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use upsert to insert or update based on product_url
            response = self.client.table(table_name).upsert(
                deal_data,
                on_conflict='product_url'
            ).execute()
            
            logger.info(f"✓ Upserted deal: {deal.get('product_name')[:50]}... to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error upserting deal to {table_name}: {e}")
            return False
    
    def upsert_deals_bulk(self, website: str, deals: List[Dict]) -> Dict[str, int]:
        """
        Bulk insert or update multiple deals
        
        Args:
            website: Name of the e-commerce website
            deals: List of deal dictionaries
            
        Returns:
            Dictionary with success and failure counts
        """
        results = {'success': 0, 'failed': 0}
        
        for deal in deals:
            if self.upsert_deal(website, deal):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        logger.info(f"Bulk upsert completed for {website}: {results['success']} succeeded, {results['failed']} failed")
        return results
    
    def get_existing_deals(self, website: str, limit: int = 100) -> List[Dict]:
        """
        Retrieve existing deals from a specific website
        
        Args:
            website: Name of the e-commerce website
            limit: Maximum number of deals to retrieve
            
        Returns:
            List of deal dictionaries
        """
        try:
            table_name = self._get_table_name(website)
            response = self.client.table(table_name).select("*").limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching deals from {table_name}: {e}")
            return []
    
    def get_deal_by_url(self, website: str, product_url: str) -> Optional[Dict]:
        """
        Check if a deal exists by product URL
        
        Args:
            website: Name of the e-commerce website
            product_url: URL of the product
            
        Returns:
            Deal dictionary if found, None otherwise
        """
        try:
            table_name = self._get_table_name(website)
            response = self.client.table(table_name).select("*").eq('product_url', product_url).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error checking deal existence: {e}")
            return None
    
    def get_deals_by_category(self, website: str, category: str, limit: int = 50) -> List[Dict]:
        """
        Get deals filtered by category
        
        Args:
            website: Name of the e-commerce website
            category: Product category
            limit: Maximum number of deals to retrieve
            
        Returns:
            List of deal dictionaries
        """
        try:
            table_name = self._get_table_name(website)
            response = self.client.table(table_name).select("*").eq('category', category).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching deals by category: {e}")
            return []
    
    def delete_old_deals(self, website: str, days_old: int = 30) -> int:
        """
        Delete deals older than specified days
        
        Args:
            website: Name of the e-commerce website
            days_old: Number of days to keep deals
            
        Returns:
            Number of deleted deals
        """
        try:
            table_name = self._get_table_name(website)
            cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.isoformat()
            
            response = self.client.table(table_name).delete().lt('collected_at', cutoff_date).execute()
            deleted_count = len(response.data) if response.data else 0
            
            logger.info(f"Deleted {deleted_count} old deals from {table_name}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting old deals: {e}")
            return 0
    
    def get_statistics(self, website: str) -> Dict:
        """
        Get statistics for deals from a specific website
        
        Args:
            website: Name of the e-commerce website
            
        Returns:
            Dictionary with statistics
        """
        try:
            table_name = self._get_table_name(website)
            response = self.client.table(table_name).select("*", count='exact').execute()
            
            stats = {
                'total_deals': response.count,
                'website': website,
                'table': table_name
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'total_deals': 0, 'website': website}


# Singleton instance
_db_instance = None

def get_db_client() -> DailyDealsDB:
    """Get or create database client singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DailyDealsDB()
    return _db_instance
