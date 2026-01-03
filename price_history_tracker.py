"""
Historical Price Tracker
=========================
Tracks price changes over time to:
- Detect genuine vs fake discounts
- Identify sudden price drops
- Calculate price trends
- Alert on historical lows

Author: AI Assistant
Date: December 2025
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

try:
    from supabase_database import get_supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not available. Price history will not be persisted.")


class PriceHistoryTracker:
    """Track and analyze product price history."""
    
    def __init__(self):
        self.client = get_supabase_client() if SUPABASE_AVAILABLE else None
    
    def record_price(self, product_url: str, price: float, mrp: Optional[float] = None, 
                    metadata: Optional[Dict] = None) -> bool:
        """
        Record a price observation for a product.
        
        Args:
            product_url: Product URL (unique identifier)
            price: Current selling price
            mrp: Maximum Retail Price
            metadata: Additional info (store, title, etc.)
        
        Returns:
            True if recorded successfully
        """
        if not self.client:
            return False
        
        try:
            data = {
                'product_url': product_url,
                'price': price,
                'mrp': mrp,
                'observed_at': datetime.now().isoformat(),
                'metadata': json.dumps(metadata or {})
            }
            
            result = self.client.table('price_history').insert(data).execute()
            return True
        
        except Exception as e:
            print(f"❌ Error recording price: {e}")
            return False
    
    def get_price_history(self, product_url: str, days: int = 30) -> List[Dict]:
        """
        Get price history for a product.
        
        Args:
            product_url: Product URL
            days: Number of days to look back
        
        Returns:
            List of price observations
        """
        if not self.client:
            return []
        
        try:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.client.table('price_history')\
                .select('*')\
                .eq('product_url', product_url)\
                .gte('observed_at', since)\
                .order('observed_at', desc=False)\
                .execute()
            
            return result.data if result.data else []
        
        except Exception as e:
            print(f"❌ Error fetching price history: {e}")
            return []
    
    def get_lowest_price(self, product_url: str, days: int = 30) -> Optional[float]:
        """Get the lowest price in the given period."""
        history = self.get_price_history(product_url, days)
        if not history:
            return None
        
        prices = [h['price'] for h in history if h.get('price')]
        return min(prices) if prices else None
    
    def get_highest_price(self, product_url: str, days: int = 30) -> Optional[float]:
        """Get the highest price in the given period."""
        history = self.get_price_history(product_url, days)
        if not history:
            return None
        
        prices = [h['price'] for h in history if h.get('price')]
        return max(prices) if prices else None
    
    def get_average_price(self, product_url: str, days: int = 30) -> Optional[float]:
        """Get the average price in the given period."""
        history = self.get_price_history(product_url, days)
        if not history:
            return None
        
        prices = [h['price'] for h in history if h.get('price')]
        return sum(prices) / len(prices) if prices else None
    
    def is_historical_low(self, product_url: str, current_price: float, days: int = 90) -> bool:
        """
        Check if current price is a historical low.
        
        Args:
            product_url: Product URL
            current_price: Current price to check
            days: Period to check (default 90 days)
        
        Returns:
            True if current price is the lowest in the period
        """
        lowest = self.get_lowest_price(product_url, days)
        if lowest is None:
            return True  # No history, consider it a potential low
        
        return current_price <= lowest
    
    def calculate_price_drop(self, product_url: str, current_price: float, days: int = 7) -> Optional[float]:
        """
        Calculate percentage price drop from recent average.
        
        Args:
            product_url: Product URL
            current_price: Current price
            days: Period for average calculation
        
        Returns:
            Percentage drop (negative means increase)
        """
        avg_price = self.get_average_price(product_url, days)
        if avg_price is None or avg_price == 0:
            return None
        
        drop_percent = ((avg_price - current_price) / avg_price) * 100
        return round(drop_percent, 2)
    
    def is_fake_discount(self, product_url: str, claimed_mrp: float, 
                        current_price: float, tolerance: float = 1.2) -> bool:
        """
        Detect fake discounts by comparing claimed MRP with historical prices.
        
        Args:
            product_url: Product URL
            claimed_mrp: The MRP claimed by seller
            current_price: Current selling price
            tolerance: Multiplier for fake detection (1.2 = 20% inflation)
        
        Returns:
            True if discount appears fake
        """
        history = self.get_price_history(product_url, days=90)
        if not history:
            return False  # No history, can't determine
        
        # Get historical selling prices (not MRP)
        past_prices = [h['price'] for h in history if h.get('price')]
        if not past_prices:
            return False
        
        avg_past_price = sum(past_prices) / len(past_prices)
        
        # If claimed MRP is much higher than past selling prices, it's suspicious
        if claimed_mrp > avg_past_price * tolerance:
            return True
        
        return False
    
    def get_price_trend(self, product_url: str, days: int = 30) -> str:
        """
        Analyze price trend.
        
        Args:
            product_url: Product URL
            days: Period to analyze
        
        Returns:
            'rising', 'falling', 'stable', or 'unknown'
        """
        history = self.get_price_history(product_url, days)
        if len(history) < 3:
            return 'unknown'
        
        # Simple trend: compare first half avg with second half avg
        mid = len(history) // 2
        first_half = [h['price'] for h in history[:mid] if h.get('price')]
        second_half = [h['price'] for h in history[mid:] if h.get('price')]
        
        if not first_half or not second_half:
            return 'unknown'
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        diff_percent = ((avg_second - avg_first) / avg_first) * 100
        
        if diff_percent > 5:
            return 'rising'
        elif diff_percent < -5:
            return 'falling'
        else:
            return 'stable'
    
    def get_price_insights(self, product_url: str, current_price: float, 
                          claimed_mrp: Optional[float] = None) -> Dict:
        """
        Get comprehensive price insights for a product.
        
        Args:
            product_url: Product URL
            current_price: Current price
            claimed_mrp: Claimed MRP (if any)
        
        Returns:
            Dictionary with insights
        """
        insights = {
            'current_price': current_price,
            'claimed_mrp': claimed_mrp,
            'has_history': False,
            'is_historical_low': False,
            'is_fake_discount': False,
            'price_drop_7d': None,
            'price_drop_30d': None,
            'lowest_30d': None,
            'highest_30d': None,
            'average_30d': None,
            'trend_30d': 'unknown',
        }
        
        history = self.get_price_history(product_url, days=30)
        if not history:
            return insights
        
        insights['has_history'] = True
        insights['is_historical_low'] = self.is_historical_low(product_url, current_price)
        insights['price_drop_7d'] = self.calculate_price_drop(product_url, current_price, days=7)
        insights['price_drop_30d'] = self.calculate_price_drop(product_url, current_price, days=30)
        insights['lowest_30d'] = self.get_lowest_price(product_url, days=30)
        insights['highest_30d'] = self.get_highest_price(product_url, days=30)
        insights['average_30d'] = self.get_average_price(product_url, days=30)
        insights['trend_30d'] = self.get_price_trend(product_url, days=30)
        
        if claimed_mrp:
            insights['is_fake_discount'] = self.is_fake_discount(
                product_url, claimed_mrp, current_price
            )
        
        return insights


# ============================================================================
# DATABASE SCHEMA (for Supabase)
# ============================================================================

PRICE_HISTORY_SCHEMA = """
-- Price History Table
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    product_url TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    mrp DECIMAL(10, 2),
    observed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_price_history_url ON price_history(product_url);
CREATE INDEX IF NOT EXISTS idx_price_history_observed ON price_history(observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_history_url_observed ON price_history(product_url, observed_at DESC);

-- Enable Row Level Security (if using Supabase)
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;

-- Policy to allow all operations (adjust based on your security needs)
CREATE POLICY "Allow all operations on price_history" ON price_history
    FOR ALL USING (true) WITH CHECK (true);
"""


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("🧪 Price History Tracker - Test Mode\n")
    
    tracker = PriceHistoryTracker()
    
    # Test URL
    test_url = "https://www.amazon.in/test-product"
    
    print("Recording test prices...")
    # Simulate price history
    tracker.record_price(test_url, 1500.0, 2000.0, {'store': 'Amazon', 'title': 'Test Product'})
    tracker.record_price(test_url, 1450.0, 2000.0, {'store': 'Amazon', 'title': 'Test Product'})
    tracker.record_price(test_url, 1400.0, 2000.0, {'store': 'Amazon', 'title': 'Test Product'})
    
    print("\nGetting insights...")
    insights = tracker.get_price_insights(test_url, 1300.0, 2000.0)
    
    print(f"\n📊 Price Insights:")
    print(f"  Current Price: ₹{insights['current_price']}")
    print(f"  Historical Low: {insights['is_historical_low']}")
    print(f"  Price Drop (7d): {insights['price_drop_7d']}%")
    print(f"  Price Trend: {insights['trend_30d']}")
    print(f"  Fake Discount: {insights['is_fake_discount']}")
    
    print("\n✅ Test completed!")
