"""
Database Module
===============
Handles saving parsed discount messages to SQLite database.

Author: AI Assistant
Date: December 2025
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, Optional, List


# Database configuration
DATABASE_FILE = 'discount_deals.db'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_FILE)


def init_database():
    """
    Initialize the database and create tables if they don't exist.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create deals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            store TEXT,
            mrp TEXT,
            discount_price TEXT,
            discount_percent TEXT,
            link TEXT NOT NULL,
            category TEXT,
            channel TEXT,
            message_id INTEGER,
            message_date TEXT,
            timestamp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(link, message_id)
        )
    ''')
    
    # Create index for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_store ON deals(store)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_category ON deals(category)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_created_at ON deals(created_at)
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {DATABASE_PATH}")


def save_to_database(data: Dict) -> bool:
    """
    Save parsed discount data to database.
    
    Args:
        data (dict): Parsed discount message data
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Extract fields
        title = data.get('title', '')
        store = data.get('store', '')
        mrp = data.get('mrp', '')
        discount_price = data.get('discount_price', '')
        discount_percent = data.get('discount_percent', '')
        link = data.get('link', '')
        category = data.get('category', '')
        channel = data.get('channel', '')
        message_id = data.get('message_id', None)
        message_date = data.get('message_date', None)
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Insert into database (ignore duplicates)
        cursor.execute('''
            INSERT OR IGNORE INTO deals (
                title, store, mrp, discount_price, discount_percent,
                link, category, channel, message_id, message_date, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, store, mrp, discount_price, discount_percent,
            link, category, channel, message_id, message_date, timestamp
        ))
        
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        return rows_affected > 0
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def get_recent_deals(limit: int = 10) -> List[Dict]:
    """
    Retrieve recent deals from database.
    
    Args:
        limit (int): Number of deals to retrieve
        
    Returns:
        list: List of deal dictionaries
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM deals
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        deals = [dict(row) for row in rows]
        
        conn.close()
        return deals
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []


def get_deals_by_store(store: str, limit: int = 10) -> List[Dict]:
    """
    Retrieve deals from a specific store.
    
    Args:
        store (str): Store name (e.g., "Amazon", "Flipkart")
        limit (int): Number of deals to retrieve
        
    Returns:
        list: List of deal dictionaries
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM deals
            WHERE store = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (store, limit))
        
        rows = cursor.fetchall()
        deals = [dict(row) for row in rows]
        
        conn.close()
        return deals
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []


def get_deals_by_category(category: str, limit: int = 10) -> List[Dict]:
    """
    Retrieve deals from a specific category.
    
    Args:
        category (str): Category name (e.g., "electronics", "fashion")
        limit (int): Number of deals to retrieve
        
    Returns:
        list: List of deal dictionaries
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM deals
            WHERE category = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (category, limit))
        
        rows = cursor.fetchall()
        deals = [dict(row) for row in rows]
        
        conn.close()
        return deals
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []


def get_statistics() -> Dict:
    """
    Get database statistics.
    
    Returns:
        dict: Statistics including total deals, deals by store, etc.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Total deals
        cursor.execute('SELECT COUNT(*) FROM deals')
        total_deals = cursor.fetchone()[0]
        
        # Deals by store
        cursor.execute('''
            SELECT store, COUNT(*) as count
            FROM deals
            GROUP BY store
            ORDER BY count DESC
        ''')
        deals_by_store = dict(cursor.fetchall())
        
        # Deals by category
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM deals
            GROUP BY category
            ORDER BY count DESC
        ''')
        deals_by_category = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_deals': total_deals,
            'deals_by_store': deals_by_store,
            'deals_by_category': deals_by_category
        }
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return {}


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE MODULE - TEST")
    print("=" * 80)
    print()
    
    # Initialize database
    init_database()
    print()
    
    # Test data
    test_deals = [
        {
            'title': 'Boat Airdopes 441',
            'store': 'Amazon',
            'mrp': '2999',
            'discount_price': '999',
            'discount_percent': '67',
            'link': 'https://amzn.to/test1',
            'category': 'electronics',
            'channel': 'amazon_deals',
            'message_id': 12345,
            'timestamp': datetime.now().isoformat()
        },
        {
            'title': 'Nike Air Max Shoes',
            'store': 'Myntra',
            'mrp': '8999',
            'discount_price': '4499',
            'discount_percent': '50',
            'link': 'https://myntra.com/test2',
            'category': 'fashion',
            'channel': 'myntra_sale',
            'message_id': 12346,
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    # Save test deals
    print("📝 Saving test deals...")
    for deal in test_deals:
        result = save_to_database(deal)
        print(f"  {'✅' if result else '❌'} {deal['title']}")
    print()
    
    # Get statistics
    print("📊 Database Statistics:")
    stats = get_statistics()
    print(f"  Total Deals: {stats.get('total_deals', 0)}")
    print(f"  By Store: {stats.get('deals_by_store', {})}")
    print(f"  By Category: {stats.get('deals_by_category', {})}")
    print()
    
    # Get recent deals
    print("📋 Recent Deals:")
    recent = get_recent_deals(limit=5)
    for i, deal in enumerate(recent, 1):
        print(f"\n  {i}. {deal['title']}")
        print(f"     Store: {deal['store']} | Price: ₹{deal['discount_price']}")
        print(f"     Link: {deal['link']}")
    
    print("\n" + "=" * 80)
    print("✅ Database test completed")
    print("=" * 80)
