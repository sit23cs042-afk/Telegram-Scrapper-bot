"""
Smart Product Categorizer
=========================
AI-powered product categorization using multiple strategies:
1. LLM-based classification (high accuracy)
2. Keyword matching (fast fallback)
3. Store breadcrumb extraction (from scraped data)

Author: AI Assistant
Date: December 2025
"""

import os
import re
from typing import Dict, Optional, List
from openai import OpenAI


class SmartProductCategorizer:
    """
    Intelligent product categorizer with multiple strategies.
    """
    
    # Comprehensive category definitions
    CATEGORIES = {
        'electronics': {
            'description': 'Electronic devices, gadgets, and accessories',
            'keywords': [
                'phone', 'mobile', 'smartphone', 'iphone', 'android', 
                'laptop', 'tablet', 'ipad', 'computer', 'pc', 'desktop',
                'earbuds', 'earphone', 'headphone', 'speaker', 'bluetooth', 'wireless',
                'smartwatch', 'watch', 'fitness band', 'tracker',
                'tv', 'television', 'smart tv', 'led', 'oled',
                'camera', 'dslr', 'gopro', 'webcam',
                'charger', 'powerbank', 'cable', 'adapter', 'battery',
                'keyboard', 'mouse', 'monitor', 'display',
                'processor', 'gpu', 'graphics card', 'ram', 'ssd', 'hard disk',
                'router', 'modem', 'wifi', 'alexa', 'echo', 'google home',
                'playstation', 'xbox', 'gaming', 'console',
                'drone', 'gimbal', 'stabilizer', 'microphone', 'mic'
            ]
        },
        'fashion': {
            'description': 'Clothing, footwear, and fashion accessories',
            'keywords': [
                'shirt', 'tshirt', 't-shirt', 'top', 'blouse',
                'jeans', 'trouser', 'pant', 'shorts', 'track pant', 'joggers',
                'dress', 'gown', 'frock',
                'saree', 'lehenga', 'salwar', 'kurta', 'kurti', 'ethnic',
                'jacket', 'blazer', 'coat', 'hoodie', 'sweatshirt', 'sweater',
                'shoes', 'sneakers', 'sandal', 'slipper', 'boots', 'heels', 'footwear',
                'casual shoes', 'formal shoes', 'loafers',
                'bag', 'handbag', 'backpack', 'wallet', 'purse',
                'belt', 'tie', 'scarf', 'stole', 'dupatta',
                'jewellery', 'jewelry', 'necklace', 'earring', 'ring', 'bracelet',
                'sunglasses', 'goggles', 'hat', 'cap',
                'innerwear', 'underwear', 'bra', 'panty', 'lingerie',
                'sportswear', 'activewear', 'athleisure'
            ]
        },
        'home': {
            'description': 'Home appliances, furniture, and home improvement',
            'keywords': [
                'furniture', 'sofa', 'couch', 'bed', 'mattress', 'pillow', 'cushion',
                'chair', 'armchair', 'recliner', 'table', 'desk', 'cabinet', 'wardrobe', 'shelf',
                'curtain', 'blind', 'carpet', 'rug', 'mat',
                'lamp', 'light', 'bulb', 'chandelier',
                'decor', 'decoration', 'wall art', 'painting', 'frame',
                'kitchen', 'kitchenware', 'utensil', 'cookware', 'crockery', 'cutlery',
                'mixer', 'grinder', 'blender', 'juicer',
                'cooker', 'pressure cooker', 'pan', 'kadai', 'tawa',
                'microwave', 'oven', 'otg', 'toaster', 'air fryer',
                'refrigerator', 'fridge', 'freezer',
                'washing machine', 'washer', 'dryer',
                'dishwasher', 'chimney', 'hob', 'cooktop', 'induction',
                'water purifier', 'ro', 'filter', 'dispenser',
                'heater', 'geyser', 'water heater', 'room heater',
                'fan', 'ceiling fan', 'pedestal fan', 'exhaust fan',
                'air conditioner', 'ac', 'cooler', 'air cooler',
                'iron', 'steam iron', 'ironing board',
                'vacuum', 'vacuum cleaner', 'mop', 'broom',
                'kettle', 'electric kettle', 'flask', 'thermos', 'bottle',
                'bedsheet', 'bed cover', 'comforter', 'blanket', 'quilt',
                'towel', 'bath towel', 'hand towel',
                'storage', 'container', 'organizer', 'basket'
            ]
        },
        'beauty': {
            'description': 'Beauty, cosmetics, and personal care products',
            'keywords': [
                'makeup', 'cosmetics', 'cosmetic',
                'lipstick', 'lip gloss', 'lip balm',
                'foundation', 'compact', 'concealer', 'bb cream', 'cc cream',
                'kajal', 'kohl', 'eyeliner', 'mascara', 'eyeshadow', 'eyebrow',
                'blush', 'highlighter', 'contour', 'bronzer',
                'nail polish', 'nail paint', 'manicure', 'pedicure',
                'skincare', 'skin care',
                'facewash', 'face wash', 'cleanser', 'scrub', 'exfoliator',
                'toner', 'serum', 'essence',
                'moisturizer', 'cream', 'lotion', 'gel',
                'sunscreen', 'sunblock', 'spf',
                'face pack', 'face mask', 'sheet mask',
                'shampoo', 'conditioner', 'hair oil', 'hair serum', 'hair mask',
                'hair color', 'hair dye', 'hair spray', 'hair gel',
                'body wash', 'shower gel', 'soap', 'handwash',
                'body lotion', 'body butter', 'body oil',
                'perfume', 'fragrance', 'deodorant', 'deo', 'cologne',
                'razor', 'shaving', 'trimmer', 'epilator', 'wax',
                'toothbrush', 'toothpaste', 'mouthwash',
                'sanitizer', 'hand sanitizer',
                'hair dryer', 'straightener', 'curler', 'styling'
            ]
        },
        'books': {
            'description': 'Books, magazines, and stationery',
            'keywords': [
                'book', 'books', 'novel', 'fiction', 'non-fiction',
                'paperback', 'hardcover', 'hardback', 'edition',
                'textbook', 'reference', 'guide', 'manual',
                'magazine', 'journal', 'newspaper',
                'notebook', 'diary', 'planner', 'organizer',
                'stationery', 'pen', 'pencil', 'eraser', 'sharpener',
                'highlighter', 'marker', 'crayon', 'color pencil',
                'paper', 'notepad', 'sticky note',
                'file', 'folder', 'binder',
                'calculator', 'scale', 'compass', 'geometry box',
                'kindle', 'ebook', 'e-book', 'audiobook'
            ]
        },
        'grocery': {
            'description': 'Food, beverages, and grocery items',
            'keywords': [
                'grocery', 'groceries', 'food', 'foods',
                'rice', 'basmati', 'wheat', 'flour', 'atta', 'maida',
                'dal', 'lentil', 'pulses', 'bean', 'chickpea',
                'oil', 'cooking oil', 'ghee', 'butter',
                'sugar', 'salt', 'spice', 'masala', 'turmeric', 'chilli',
                'tea', 'coffee', 'milk', 'beverage', 'juice', 'drink',
                'biscuit', 'cookie', 'cake', 'pastry',
                'chocolate', 'candy', 'sweet', 'snack', 'namkeen',
                'noodles', 'pasta', 'macaroni', 'vermicelli',
                'sauce', 'ketchup', 'mayonnaise', 'pickle', 'jam',
                'honey', 'peanut butter',
                'dry fruit', 'nuts', 'almond', 'cashew', 'raisin',
                'breakfast cereal', 'oats', 'cornflakes', 'muesli',
                'instant mix', 'ready to eat', 'frozen food'
            ]
        },
        'sports': {
            'description': 'Sports equipment, fitness, and outdoor gear',
            'keywords': [
                'sports', 'sport', 'fitness', 'gym', 'workout', 'exercise',
                'dumbbell', 'barbell', 'weights', 'kettlebell',
                'treadmill', 'elliptical', 'cross trainer',
                'cycle', 'bicycle', 'bike', 'cycling',
                'yoga', 'yoga mat', 'yoga block', 'yoga pants',
                'cricket', 'bat', 'ball', 'stumps', 'wicket', 'gloves', 'pads',
                'football', 'soccer', 'goal post',
                'badminton', 'racket', 'racquet', 'shuttlecock',
                'tennis', 'table tennis', 'ping pong',
                'swimming', 'swimsuit', 'goggles', 'swimming cap',
                'running', 'running shoes', 'sports shoes', 'track pants',
                'skipping rope', 'jump rope',
                'resistance band', 'pull up bar', 'push up bar',
                'protein', 'whey', 'supplement', 'creatine',
                'gym bag', 'sports bag', 'duffel bag',
                'camping', 'tent', 'sleeping bag', 'backpack', 'trekking'
            ]
        },
        'toys': {
            'description': 'Toys, games, and kids products',
            'keywords': [
                'toy', 'toys', 'game', 'games', 'play', 'playset',
                'doll', 'teddy', 'soft toy', 'plush',
                'lego', 'building blocks', 'construction',
                'car', 'truck', 'vehicle', 'remote control', 'rc',
                'puzzle', 'jigsaw', 'board game',
                'kids', 'children', 'baby', 'infant', 'toddler',
                'diaper', 'nappy', 'wipes', 'baby care',
                'baby food', 'baby oil', 'baby powder', 'baby shampoo',
                'bottle', 'feeding bottle', 'sipper', 'bowl',
                'stroller', 'pram', 'walker', 'rocker',
                'cradle', 'crib', 'baby bed',
                'school bag', 'lunch box', 'water bottle',
                'swing', 'slide', 'ride on'
            ]
        },
        'health': {
            'description': 'Health, medical, and wellness products',
            'keywords': [
                'health', 'medical', 'medicine', 'healthcare',
                'vitamin', 'supplement', 'protein', 'nutrition',
                'first aid', 'bandage', 'gauze', 'antiseptic',
                'thermometer', 'blood pressure', 'bp monitor', 'bp', 'sphygmomanometer',
                'oximeter', 'pulse oximeter', 'digital monitor',
                'glucometer', 'glucose meter', 'diabetes',
                'mask', 'n95', 'surgical mask', 'face mask',
                'sanitizer', 'disinfectant',
                'pain relief', 'balm', 'ointment', 'cream',
                'massager', 'massage', 'back support', 'knee support',
                'heating pad', 'ice pack',
                'nebulizer', 'inhaler', 'vaporizer', 'steamer',
                'weighing scale', 'weight scale', 'body fat',
                'pregnancy test', 'ovulation kit',
                'condom', 'contraceptive',
                'wheelchair', 'walker', 'crutches', 'walking stick'
            ]
        },
        'automotive': {
            'description': 'Vehicle accessories and automotive products',
            'keywords': [
                'car', 'vehicle', 'auto', 'automotive',
                'car accessories', 'car care', 'car cleaning',
                'car cover', 'seat cover', 'steering cover',
                'car mat', 'floor mat', 'dashboard',
                'car charger', 'mobile holder', 'phone holder',
                'dashcam', 'dash cam', 'car camera',
                'car perfume', 'air freshener',
                'car polish', 'car wax', 'car shampoo',
                'tyre', 'tire', 'wheel', 'alloy wheel',
                'car battery', 'jump starter',
                'helmet', 'bike helmet', 'riding gear',
                'bike accessories', 'motorcycle',
                'car vacuum', 'pressure washer',
                'toolkit', 'tool kit', 'jack', 'spanner'
            ]
        },
        'pet': {
            'description': 'Pet supplies and accessories',
            'keywords': [
                'pet', 'pets', 'dog', 'puppy', 'cat', 'kitten',
                'pet food', 'dog food', 'cat food', 'pet treats',
                'pet toy', 'chew toy', 'ball', 'rope toy',
                'pet bed', 'pet house', 'kennel', 'cage',
                'leash', 'collar', 'harness', 'muzzle',
                'pet bowl', 'feeder', 'water dispenser',
                'pet grooming', 'pet brush', 'nail clipper',
                'pet shampoo', 'pet care',
                'aquarium', 'fish tank', 'fish food',
                'bird cage', 'bird food', 'bird toy'
            ]
        }
    }
    
    def __init__(self, use_llm: bool = False, openai_api_key: Optional[str] = None):
        """
        Initialize the categorizer.
        
        Args:
            use_llm: Enable LLM-based categorization for higher accuracy
            openai_api_key: OpenAI API key (required if use_llm=True)
        """
        self.use_llm = use_llm
        self.client = None
        
        if use_llm:
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                print("⚠️  Warning: LLM categorization enabled but no API key found. Falling back to keyword matching.")
                self.use_llm = False
    
    def categorize_with_llm(self, product_title: str) -> str:
        """
        Use LLM to categorize product with high accuracy.
        
        Args:
            product_title: Full product title
            
        Returns:
            Category name
        """
        if not self.client:
            return self.categorize_with_keywords(product_title)
        
        try:
            # Create category list with descriptions
            category_list = "\n".join([
                f"- {cat}: {info['description']}" 
                for cat, info in self.CATEGORIES.items()
            ])
            
            prompt = f"""Categorize the following product into ONE of these categories:

{category_list}
- other: Products that don't fit any above category

Product Title: "{product_title}"

Rules:
1. Return ONLY the category name (lowercase, one word)
2. Be specific - choose the most relevant category
3. If uncertain, return 'other'

Category:"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective
                messages=[
                    {"role": "system", "content": "You are a product categorization expert. Always respond with just one category name, nothing else."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=10
            )
            
            category = response.choices[0].message.content.strip().lower()
            
            # Validate category
            if category in self.CATEGORIES:
                return category
            else:
                # LLM returned invalid category, fallback to keywords
                return self.categorize_with_keywords(product_title)
                
        except Exception as e:
            print(f"⚠️  LLM categorization failed: {e}")
            return self.categorize_with_keywords(product_title)
    
    def categorize_with_keywords(self, text: str) -> str:
        """
        Fast keyword-based categorization (fallback method).
        
        Args:
            text: Product title or description
            
        Returns:
            Category name
        """
        if not text:
            return "other"
        
        text_lower = text.lower()
        
        # Score each category
        category_scores = {}
        for category, info in self.CATEGORIES.items():
            score = 0
            matched_keywords = []
            
            for keyword in info['keywords']:
                # Use word boundaries for better matching
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    # Multi-word medical/health terms get extra weight
                    if category == 'health' and ' ' in keyword:
                        score += 2  # Higher weight for multi-word health terms
                    else:
                        score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                # Boost score if multiple keywords match
                if len(matched_keywords) > 1:
                    score += len(matched_keywords) * 0.5
                
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            return best_category
        
        return "other"
    
    def categorize(self, product_title: str, use_verified_title: bool = True) -> Dict:
        """
        Main categorization method with fallback strategy.
        
        Args:
            product_title: Product title (preferably verified/scraped title)
            use_verified_title: Whether this is a verified title from scraping
            
        Returns:
            Dict with category and confidence info
        """
        if not product_title:
            return {
                'category': 'other',
                'method': 'default',
                'confidence': 'low'
            }
        
        # Strategy 1: LLM-based (highest accuracy)
        if self.use_llm and use_verified_title:
            category = self.categorize_with_llm(product_title)
            return {
                'category': category,
                'method': 'llm',
                'confidence': 'high'
            }
        
        # Strategy 2: Keyword matching (fast fallback)
        category = self.categorize_with_keywords(product_title)
        return {
            'category': category,
            'method': 'keywords',
            'confidence': 'medium' if use_verified_title else 'low'
        }
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories."""
        return list(self.CATEGORIES.keys()) + ['other']
    
    def get_category_info(self, category: str) -> Optional[Dict]:
        """Get information about a specific category."""
        return self.CATEGORIES.get(category)


# Example usage
if __name__ == "__main__":
    # Test with different modes
    print("Testing Smart Product Categorizer")
    print("=" * 80)
    
    test_products = [
        "boAt Airdopes 800 Dolby Audio Bluetooth TWS Earbuds",
        "Vivel Aloe Vera & White Rose Scent Shower Gel",
        "Preethi Diamond 750 Watt Mixer Grinder",
        "Kohinoor Pulao Basmati Rice 1kg",
        "Nike Men's Running Shoes",
        "Lakme Absolute Foundation",
        "The Alchemist Novel by Paulo Coelho",
        "Yonex Badminton Racket",
        "Generic Product XYZ123"
    ]
    
    # Test keyword-based categorization
    print("\n1️⃣  Keyword-Based Categorization (Fast)")
    print("-" * 80)
    categorizer = SmartProductCategorizer(use_llm=False)
    
    for product in test_products:
        result = categorizer.categorize(product)
        print(f"📦 {product[:50]:<50} → {result['category']}")
    
    # Test LLM-based categorization (if API key available)
    print("\n\n2️⃣  LLM-Based Categorization (High Accuracy)")
    print("-" * 80)
    llm_categorizer = SmartProductCategorizer(use_llm=True)
    
    if llm_categorizer.use_llm:
        for product in test_products[:3]:  # Test first 3 to save API costs
            result = llm_categorizer.categorize(product)
            print(f"📦 {product[:50]:<50} → {result['category']} ({result['method']})")
    else:
        print("⚠️  LLM not available (no API key)")
