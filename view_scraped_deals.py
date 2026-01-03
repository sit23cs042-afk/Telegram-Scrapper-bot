"""
Quick script to view scraped deals from database
"""
from database.supabase_client import DailyDealsDB
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def view_deals():
    """View all deals from database"""
    db = DailyDealsDB()  # No arguments needed
    
    print("\n" + "="*80)
    print("📦 AMAZON DEALS")
    print("="*80)
    
    amazon_deals = db.client.table('amazon_deals').select('*').limit(5).execute()
    for i, deal in enumerate(amazon_deals.data, 1):
        print(f"\n{i}. {deal.get('product_name', 'N/A')[:60]}")
        print(f"   Price: ₹{deal.get('discounted_price', 'N/A')}")
        print(f"   Discount: {deal.get('discount_percentage', 0)}%")
        print(f"   URL: {deal.get('product_url', 'N/A')[:80]}...")
    
    print("\n" + "="*80)
    print("📱 FLIPKART DEALS")
    print("="*80)
    
    flipkart_deals = db.client.table('flipkart_deals').select('*').limit(5).execute()
    for i, deal in enumerate(flipkart_deals.data, 1):
        print(f"\n{i}. {deal.get('product_name', 'N/A')[:60]}")
        print(f"   Price: ₹{deal.get('discounted_price', 'N/A')}")
        print(f"   Category: {deal.get('category', 'N/A')}")
        print(f"   URL: {deal.get('product_url', 'N/A')[:80]}...")
    
    # Get total counts
    amazon_total = db.client.table('amazon_deals').select('id', count='exact').execute()
    flipkart_total = db.client.table('flipkart_deals').select('id', count='exact').execute()
    
    print("\n" + "="*80)
    print(f"Total Deals in Database:")
    print(f"  Amazon: {amazon_total.count} deals")
    print(f"  Flipkart: {flipkart_total.count} deals")
    print("="*80 + "\n")

if __name__ == "__main__":
    view_deals()
