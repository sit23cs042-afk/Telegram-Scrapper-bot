"""
Duplicate Deal Detector
=======================
Detects and handles duplicate deals across multiple sources:
- Same product from different channels
- Same product from different platforms
- Price variations of same product
- URL normalization and matching

Author: AI Assistant
Date: December 2025
"""

from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode
import re
from difflib import SequenceMatcher
import hashlib


class DuplicateDetector:
    """Detect duplicate deals across sources."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_threshold: Title similarity threshold (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL for comparison.
        Removes tracking parameters and standardizes format.
        
        Args:
            url: Product URL
        
        Returns:
            Normalized URL
        """
        if not url:
            return ""
        
        # Parse URL
        parsed = urlparse(url.lower())
        
        # Extract domain
        domain = parsed.netloc
        
        # Platform-specific normalization
        if 'amazon' in domain:
            return self._normalize_amazon_url(parsed)
        elif 'flipkart' in domain:
            return self._normalize_flipkart_url(parsed)
        elif 'myntra' in domain:
            return self._normalize_myntra_url(parsed)
        else:
            # Generic normalization
            path = parsed.path.rstrip('/')
            return f"{domain}{path}"
    
    def _normalize_amazon_url(self, parsed) -> str:
        """Normalize Amazon URL to product ID."""
        path = parsed.path
        
        # Extract ASIN (Amazon Standard Identification Number)
        # Pattern: /dp/ASIN or /gp/product/ASIN
        asin_match = re.search(r'/(dp|gp/product)/([A-Z0-9]{10})', path)
        if asin_match:
            asin = asin_match.group(2)
            return f"amazon.in/dp/{asin}"
        
        return f"{parsed.netloc}{path}"
    
    def _normalize_flipkart_url(self, parsed) -> str:
        """Normalize Flipkart URL to product ID."""
        path = parsed.path
        
        # Extract product ID from URL
        # Pattern: /product-name/p/itm... or ?pid=...
        pid_match = re.search(r'/p/(itm[a-z0-9]+)', path, re.I)
        if pid_match:
            pid = pid_match.group(1)
            return f"flipkart.com/p/{pid}"
        
        # Check query parameters
        query_params = parse_qs(parsed.query)
        if 'pid' in query_params:
            pid = query_params['pid'][0]
            return f"flipkart.com/pid/{pid}"
        
        return f"{parsed.netloc}{path}"
    
    def _normalize_myntra_url(self, parsed) -> str:
        """Normalize Myntra URL to product ID."""
        path = parsed.path
        
        # Extract product ID
        # Pattern: /product-name/12345
        pid_match = re.search(r'/(\d+)$', path)
        if pid_match:
            pid = pid_match.group(1)
            return f"myntra.com/{pid}"
        
        return f"{parsed.netloc}{path}"
    
    def normalize_title(self, title: str) -> str:
        """
        Normalize product title for comparison.
        
        Args:
            title: Product title
        
        Returns:
            Normalized title
        """
        if not title:
            return ""
        
        # Convert to lowercase
        title = title.lower()
        
        # Remove special characters but keep alphanumeric and spaces
        title = re.sub(r'[^\w\s]', ' ', title)
        
        # Remove extra spaces
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Remove common stopwords
        stopwords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
        words = title.split()
        words = [w for w in words if w not in stopwords]
        
        return ' '.join(words)
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two titles.
        
        Args:
            title1: First title
            title2: Second title
        
        Returns:
            Similarity score (0-1)
        """
        if not title1 or not title2:
            return 0.0
        
        # Normalize titles
        norm1 = self.normalize_title(title1)
        norm2 = self.normalize_title(title2)
        
        # Calculate sequence similarity
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def calculate_price_similarity(self, price1: float, price2: float, tolerance: float = 0.05) -> bool:
        """
        Check if two prices are similar (within tolerance).
        
        Args:
            price1: First price
            price2: Second price
            tolerance: Tolerance percentage (default 5%)
        
        Returns:
            True if prices are similar
        """
        if not price1 or not price2:
            return False
        
        # Calculate percentage difference
        avg_price = (price1 + price2) / 2
        diff = abs(price1 - price2)
        diff_pct = (diff / avg_price) if avg_price > 0 else 0
        
        return diff_pct <= tolerance
    
    def is_duplicate(self, deal1: Dict, deal2: Dict) -> Tuple[bool, str]:
        """
        Check if two deals are duplicates.
        
        Args:
            deal1: First deal
            deal2: Second deal
        
        Returns:
            Tuple of (is_duplicate: bool, reason: str)
        """
        # Check 1: Exact URL match
        url1 = self.normalize_url(deal1.get('url', ''))
        url2 = self.normalize_url(deal2.get('url', ''))
        
        if url1 and url2 and url1 == url2:
            return True, "Exact URL match"
        
        # Check 2: Title similarity + price similarity
        title1 = deal1.get('title', '')
        title2 = deal2.get('title', '')
        title_sim = self.calculate_title_similarity(title1, title2)
        
        if title_sim >= self.similarity_threshold:
            # Check prices if available
            price1 = deal1.get('price') or deal1.get('offer_price')
            price2 = deal2.get('price') or deal2.get('offer_price')
            
            if price1 and price2:
                # Extract numeric values if strings
                if isinstance(price1, str):
                    price1 = float(re.sub(r'[^\d.]', '', price1) or 0)
                if isinstance(price2, str):
                    price2 = float(re.sub(r'[^\d.]', '', price2) or 0)
                
                if self.calculate_price_similarity(price1, price2):
                    return True, f"Title similarity: {title_sim:.2f}, Similar price"
        
        # Check 3: Same store + high title similarity
        store1 = deal1.get('store', '').lower()
        store2 = deal2.get('store', '').lower()
        
        if store1 and store2 and store1 == store2 and title_sim >= 0.75:
            return True, f"Same store, Title similarity: {title_sim:.2f}"
        
        return False, "Not duplicate"
    
    def find_duplicates(self, deals: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Find all duplicate deals in a list.
        
        Args:
            deals: List of deal dictionaries
        
        Returns:
            Dictionary mapping unique_id to list of duplicate deals
        """
        duplicate_groups = {}
        processed = set()
        
        for i, deal1 in enumerate(deals):
            if i in processed:
                continue
            
            # Create group for this deal
            group_id = self._generate_deal_hash(deal1)
            group = [deal1]
            
            # Find duplicates
            for j, deal2 in enumerate(deals[i+1:], start=i+1):
                if j in processed:
                    continue
                
                is_dup, reason = self.is_duplicate(deal1, deal2)
                if is_dup:
                    group.append(deal2)
                    processed.add(j)
            
            # Add group if has duplicates
            if len(group) > 1:
                duplicate_groups[group_id] = group
            
            processed.add(i)
        
        return duplicate_groups
    
    def deduplicate(self, deals: List[Dict], strategy: str = 'best') -> List[Dict]:
        """
        Remove duplicates from deal list.
        
        Args:
            deals: List of deal dictionaries
            strategy: Deduplication strategy:
                - 'best': Keep best deal (lowest price, highest score)
                - 'first': Keep first occurrence
                - 'merge': Merge information from duplicates
        
        Returns:
            Deduplicated list of deals
        """
        duplicate_groups = self.find_duplicates(deals)
        
        # Track which deals to keep
        keep_indices = set(range(len(deals)))
        
        for group in duplicate_groups.values():
            if strategy == 'best':
                best_deal = self._select_best_deal(group)
                # Remove all except best
                for deal in group:
                    if deal is not best_deal:
                        try:
                            idx = deals.index(deal)
                            keep_indices.discard(idx)
                        except ValueError:
                            pass
            
            elif strategy == 'first':
                # Keep first, remove rest
                for deal in group[1:]:
                    try:
                        idx = deals.index(deal)
                        keep_indices.discard(idx)
                    except ValueError:
                        pass
            
            elif strategy == 'merge':
                merged_deal = self._merge_deals(group)
                # Replace first with merged, remove rest
                first_idx = deals.index(group[0])
                deals[first_idx] = merged_deal
                for deal in group[1:]:
                    try:
                        idx = deals.index(deal)
                        keep_indices.discard(idx)
                    except ValueError:
                        pass
        
        # Return deduplicated list
        return [deals[i] for i in sorted(keep_indices)]
    
    def _select_best_deal(self, group: List[Dict]) -> Dict:
        """Select best deal from duplicate group."""
        # Priority: lowest final price, then highest score, then first
        best = group[0]
        
        for deal in group[1:]:
            # Compare final effective price
            price_best = deal.get('final_effective_price') or deal.get('price') or deal.get('offer_price') or float('inf')
            price_current = best.get('final_effective_price') or best.get('price') or best.get('offer_price') or float('inf')
            
            # Extract numeric values if strings
            if isinstance(price_best, str):
                price_best = float(re.sub(r'[^\d.]', '', price_best) or 'inf')
            if isinstance(price_current, str):
                price_current = float(re.sub(r'[^\d.]', '', price_current) or 'inf')
            
            if price_best < price_current:
                best = deal
            elif price_best == price_current:
                # Compare scores
                score_best = deal.get('score', 0)
                score_current = best.get('score', 0)
                if score_best > score_current:
                    best = deal
        
        return best
    
    def _merge_deals(self, group: List[Dict]) -> Dict:
        """Merge information from duplicate deals."""
        merged = group[0].copy()
        
        # Collect all sources
        sources = [merged.get('source', 'unknown')]
        for deal in group[1:]:
            source = deal.get('source', 'unknown')
            if source not in sources:
                sources.append(source)
        
        merged['sources'] = sources
        merged['duplicate_count'] = len(group)
        
        # Take best price
        prices = []
        for deal in group:
            price = deal.get('final_effective_price') or deal.get('price') or deal.get('offer_price')
            if price:
                if isinstance(price, str):
                    price = float(re.sub(r'[^\d.]', '', price) or 0)
                if price > 0:
                    prices.append(price)
        
        if prices:
            merged['best_price'] = min(prices)
            merged['price_range'] = {'min': min(prices), 'max': max(prices)}
        
        return merged
    
    def _generate_deal_hash(self, deal: Dict) -> str:
        """Generate unique hash for deal."""
        url = self.normalize_url(deal.get('url', ''))
        title = self.normalize_title(deal.get('title', ''))
        
        hash_str = f"{url}_{title}"
        return hashlib.md5(hash_str.encode()).hexdigest()[:16]


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("🧪 Duplicate Deal Detector - Test Mode\n")
    
    detector = DuplicateDetector()
    
    # Test deals with duplicates
    test_deals = [
        {
            'title': 'Apple iPhone 15 Pro 256GB',
            'price': 119900,
            'url': 'https://www.amazon.in/dp/B0CHX1W1XY',
            'store': 'Amazon',
            'source': 'telegram_channel_1'
        },
        {
            'title': 'Apple iPhone 15 Pro (256GB) - Blue Titanium',
            'price': 119900,
            'url': 'https://www.amazon.in/dp/B0CHX1W1XY?ref=xyz',
            'store': 'Amazon',
            'source': 'telegram_channel_2'
        },
        {
            'title': 'Samsung Galaxy S24 Ultra',
            'price': 99999,
            'url': 'https://www.flipkart.com/product/xyz',
            'store': 'Flipkart',
            'source': 'official_deal_page'
        },
        {
            'title': 'OnePlus 12 5G',
            'price': 54999,
            'url': 'https://www.amazon.in/dp/ABCDEFGHIJ',
            'store': 'Amazon',
            'source': 'telegram_channel_3'
        }
    ]
    
    print(f"Testing with {len(test_deals)} deals...\n")
    
    # Find duplicates
    duplicates = detector.find_duplicates(test_deals)
    print(f"Found {len(duplicates)} duplicate groups:\n")
    
    for group_id, group in duplicates.items():
        print(f"Group {group_id}:")
        for deal in group:
            print(f"  - {deal['title']} ({deal['source']})")
        print()
    
    # Deduplicate
    deduplicated = detector.deduplicate(test_deals, strategy='best')
    print(f"\nAfter deduplication: {len(deduplicated)} unique deals")
    
    print("\n✅ Test completed!")
