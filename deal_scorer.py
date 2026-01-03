"""
Deal Scoring System
===================
Scores deals on a 0-100 scale based on multiple factors:
- Discount authenticity (historical price comparison)
- Discount percentage
- Product popularity (ratings, reviews)
- Deal urgency (limited time, flash deals)
- Seller trustworthiness
- Price competitiveness

Author: AI Assistant
Date: December 2025
"""

from typing import Dict, Optional
import re


class DealScorer:
    """
    Comprehensive deal scoring system (0-100).
    Higher scores indicate better deals.
    """
    
    # Scoring weights
    WEIGHTS = {
        'discount_authenticity': 25,  # Is the discount real?
        'discount_percentage': 20,    # How much discount?
        'product_popularity': 15,     # Ratings & reviews
        'deal_urgency': 15,          # Flash/limited time
        'price_competitiveness': 15,  # Historical low?
        'seller_trust': 10,          # Official/verified seller
    }
    
    def __init__(self):
        """Initialize scorer."""
        pass
    
    def score_deal(self, deal_data: Dict, price_insights: Optional[Dict] = None) -> Dict:
        """
        Calculate comprehensive deal score.
        
        Args:
            deal_data: Deal information including:
                - discount_percent: Claimed discount %
                - price: Current price
                - mrp: Original price
                - rating: Product rating (0-5)
                - review_count: Number of reviews
                - deal_type: 'flash', 'regular', 'festival', etc.
                - seller_type: 'official', 'verified', 'third_party'
                - stock_status: 'in_stock', 'low_stock', 'out_of_stock'
            price_insights: Historical price insights from PriceHistoryTracker
        
        Returns:
            Dictionary with score and breakdown
        """
        scores = {}
        
        # 1. Discount Authenticity (25 points)
        scores['discount_authenticity'] = self._score_discount_authenticity(
            deal_data, price_insights
        )
        
        # 2. Discount Percentage (20 points)
        scores['discount_percentage'] = self._score_discount_percentage(
            deal_data.get('discount_percent', 0)
        )
        
        # 3. Product Popularity (15 points)
        scores['product_popularity'] = self._score_popularity(
            deal_data.get('rating', 0),
            deal_data.get('review_count', 0)
        )
        
        # 4. Deal Urgency (15 points)
        scores['deal_urgency'] = self._score_urgency(
            deal_data.get('deal_type', 'regular'),
            deal_data.get('stock_status', 'in_stock')
        )
        
        # 5. Price Competitiveness (15 points)
        scores['price_competitiveness'] = self._score_price_competitiveness(
            price_insights
        )
        
        # 6. Seller Trust (10 points)
        scores['seller_trust'] = self._score_seller_trust(
            deal_data.get('seller_type', 'third_party')
        )
        
        # Calculate total score
        total_score = sum(scores.values())
        
        return {
            'total_score': round(total_score, 1),
            'grade': self._get_grade(total_score),
            'breakdown': scores,
            'recommendation': self._get_recommendation(total_score)
        }
    
    def _score_discount_authenticity(self, deal_data: Dict, 
                                     price_insights: Optional[Dict]) -> float:
        """
        Score discount authenticity (0-25 points).
        Uses historical price data to detect fake discounts.
        """
        if not price_insights or not price_insights.get('has_history'):
            # No history - use basic validation
            discount = deal_data.get('discount_percent', 0)
            if discount > 80:  # Suspiciously high
                return 10.0
            elif discount > 50:
                return 15.0
            elif discount > 20:
                return 20.0
            else:
                return 15.0
        
        # Have historical data
        score = 25.0
        
        # Penalize fake discounts heavily
        if price_insights.get('is_fake_discount'):
            score -= 15.0
        
        # Reward historical lows
        if price_insights.get('is_historical_low'):
            score = min(score + 5.0, 25.0)
        
        # Consider price trend
        trend = price_insights.get('trend_30d', 'unknown')
        if trend == 'falling':
            score = min(score + 2.0, 25.0)
        elif trend == 'rising':
            score = max(score - 2.0, 0)
        
        return round(max(0, min(score, 25.0)), 1)
    
    def _score_discount_percentage(self, discount_percent: float) -> float:
        """
        Score based on discount percentage (0-20 points).
        """
        # Extract numeric value if string
        if isinstance(discount_percent, str):
            match = re.search(r'(\d+(?:\.\d+)?)', discount_percent)
            if match:
                discount_percent = float(match.group(1))
            else:
                discount_percent = 0
        
        discount = float(discount_percent)
        
        # Score brackets
        if discount >= 70:
            return 20.0
        elif discount >= 60:
            return 18.0
        elif discount >= 50:
            return 16.0
        elif discount >= 40:
            return 14.0
        elif discount >= 30:
            return 12.0
        elif discount >= 20:
            return 10.0
        elif discount >= 10:
            return 6.0
        elif discount >= 5:
            return 3.0
        else:
            return 0.0
    
    def _score_popularity(self, rating: float, review_count: int) -> float:
        """
        Score based on product popularity (0-15 points).
        """
        score = 0.0
        
        # Rating component (0-10 points)
        if isinstance(rating, (int, float)) and rating > 0:
            # Convert to 0-10 scale
            score += (rating / 5.0) * 10.0
        
        # Review count component (0-5 points)
        if review_count >= 10000:
            score += 5.0
        elif review_count >= 5000:
            score += 4.5
        elif review_count >= 1000:
            score += 4.0
        elif review_count >= 500:
            score += 3.5
        elif review_count >= 100:
            score += 3.0
        elif review_count >= 50:
            score += 2.0
        elif review_count >= 10:
            score += 1.0
        
        return round(min(score, 15.0), 1)
    
    def _score_urgency(self, deal_type: str, stock_status: str) -> float:
        """
        Score based on deal urgency (0-15 points).
        """
        score = 0.0
        
        # Deal type scoring (0-10 points)
        deal_type_lower = deal_type.lower() if deal_type else ''
        
        if any(x in deal_type_lower for x in ['lightning', 'flash', 'limited']):
            score += 10.0
        elif any(x in deal_type_lower for x in ['festival', 'sale', 'special']):
            score += 8.0
        elif any(x in deal_type_lower for x in ['daily', 'today']):
            score += 6.0
        else:
            score += 3.0
        
        # Stock status scoring (0-5 points)
        stock_lower = stock_status.lower() if stock_status else ''
        
        if 'low' in stock_lower or 'limited' in stock_lower:
            score += 5.0
        elif 'in_stock' in stock_lower or 'available' in stock_lower:
            score += 3.0
        elif 'out' in stock_lower:
            score = 0.0  # No points if out of stock
        
        return round(min(score, 15.0), 1)
    
    def _score_price_competitiveness(self, price_insights: Optional[Dict]) -> float:
        """
        Score based on price competitiveness (0-15 points).
        """
        if not price_insights or not price_insights.get('has_history'):
            return 7.5  # Neutral score without history
        
        score = 7.5  # Base score
        
        # Historical low bonus
        if price_insights.get('is_historical_low'):
            score += 5.0
        
        # Price drop bonus
        drop_7d = price_insights.get('price_drop_7d', 0) or 0
        drop_30d = price_insights.get('price_drop_30d', 0) or 0
        
        if drop_7d > 20:
            score += 2.5
        elif drop_7d > 10:
            score += 1.5
        elif drop_7d > 5:
            score += 0.5
        
        if drop_30d > 30:
            score += 2.5
        elif drop_30d > 20:
            score += 1.5
        elif drop_30d > 10:
            score += 0.5
        
        return round(min(score, 15.0), 1)
    
    def _score_seller_trust(self, seller_type: str) -> float:
        """
        Score based on seller trustworthiness (0-10 points).
        """
        seller_lower = seller_type.lower() if seller_type else ''
        
        if any(x in seller_lower for x in ['official', 'brand', 'manufacturer']):
            return 10.0
        elif any(x in seller_lower for x in ['verified', 'authorized', 'plus', 'assured']):
            return 8.0
        elif any(x in seller_lower for x in ['platform', 'fulfilled']):
            return 6.0
        else:
            return 3.0  # Third-party sellers
    
    def _get_grade(self, score: float) -> str:
        """
        Convert numeric score to letter grade.
        """
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def _get_recommendation(self, score: float) -> str:
        """
        Get recommendation based on score.
        """
        if score >= 85:
            return "🔥 Excellent Deal! Highly Recommended"
        elif score >= 75:
            return "✅ Great Deal! Worth Buying"
        elif score >= 65:
            return "👍 Good Deal! Consider It"
        elif score >= 55:
            return "⚠️ Average Deal - Check Alternatives"
        elif score >= 40:
            return "❌ Below Average - Not Recommended"
        else:
            return "🚫 Poor Deal - Avoid"
    
    def score_multiple_deals(self, deals: list) -> list:
        """
        Score multiple deals and sort by score.
        
        Args:
            deals: List of deal dictionaries
        
        Returns:
            List of deals with scores, sorted by score (highest first)
        """
        scored_deals = []
        
        for deal in deals:
            score_data = self.score_deal(deal, deal.get('price_insights'))
            deal['score'] = score_data['total_score']
            deal['grade'] = score_data['grade']
            deal['recommendation'] = score_data['recommendation']
            deal['score_breakdown'] = score_data['breakdown']
            scored_deals.append(deal)
        
        # Sort by score (highest first)
        scored_deals.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return scored_deals


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("🧪 Deal Scoring System - Test Mode\n")
    
    scorer = DealScorer()
    
    # Test deals
    test_deals = [
        {
            'title': 'iPhone 15 Pro',
            'discount_percent': 15,
            'price': 119900,
            'mrp': 139900,
            'rating': 4.5,
            'review_count': 5000,
            'deal_type': 'Lightning Deal',
            'seller_type': 'official',
            'stock_status': 'low_stock',
        },
        {
            'title': 'Generic Headphones',
            'discount_percent': 80,
            'price': 299,
            'mrp': 1499,
            'rating': 3.2,
            'review_count': 50,
            'deal_type': 'regular',
            'seller_type': 'third_party',
            'stock_status': 'in_stock',
        },
        {
            'title': 'Samsung Smart TV',
            'discount_percent': 40,
            'price': 35999,
            'mrp': 59999,
            'rating': 4.3,
            'review_count': 3500,
            'deal_type': 'Festival Sale',
            'seller_type': 'verified',
            'stock_status': 'in_stock',
            'price_insights': {
                'has_history': True,
                'is_historical_low': True,
                'is_fake_discount': False,
                'price_drop_7d': 15.5,
                'price_drop_30d': 25.0,
                'trend_30d': 'falling'
            }
        }
    ]
    
    # Score deals
    print("Scoring deals...\n")
    scored = scorer.score_multiple_deals(test_deals)
    
    # Display results
    for i, deal in enumerate(scored, 1):
        print(f"{i}. {deal['title']}")
        print(f"   Score: {deal['score']}/100 (Grade: {deal['grade']})")
        print(f"   {deal['recommendation']}")
        print(f"   Breakdown: {deal['score_breakdown']}")
        print()
    
    print("✅ Test completed!")
