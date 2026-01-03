"""
View Deals - Query Tool
=======================
Simple script to view and query deals from the database.
"""

from database import (
    get_recent_deals, 
    get_deals_by_store, 
    get_deals_by_category,
    get_statistics
)


def main():
    print("\n" + "=" * 80)
    print("📊 DISCOUNT DEALS DATABASE VIEWER")
    print("=" * 80 + "\n")
    
    # Get statistics
    print("📈 DATABASE STATISTICS")
    print("-" * 80)
    stats = get_statistics()
    
    print(f"Total Deals: {stats.get('total_deals', 0)}")
    print()
    
    if stats.get('deals_by_store'):
        print("Deals by Store:")
        for store, count in stats['deals_by_store'].items():
            print(f"  • {store}: {count}")
    print()
    
    if stats.get('deals_by_category'):
        print("Deals by Category:")
        for category, count in stats['deals_by_category'].items():
            print(f"  • {category}: {count}")
    print()
    
    # Get recent deals
    print("\n" + "=" * 80)
    print("🔥 RECENT DEALS (Last 10)")
    print("=" * 80 + "\n")
    
    recent = get_recent_deals(10)
    
    if not recent:
        print("⚠️  No deals found in database yet.")
        print("💡 Keep the telegram_listener.py running to collect deals!")
    else:
        for i, deal in enumerate(recent, 1):
            print(f"\n{i}. 🏷️  {deal['title']}")
            print(f"   🏪 Store: {deal['store']}")
            
            if deal['mrp'] and deal['discount_price']:
                print(f"   💰 Price: ₹{deal['discount_price']} (was ₹{deal['mrp']})")
            elif deal['discount_price']:
                print(f"   💰 Price: ₹{deal['discount_price']}")
            
            if deal['discount_percent']:
                print(f"   🎯 Discount: {deal['discount_percent']}% OFF")
            
            print(f"   🔗 Link: {deal['link']}")
            print(f"   📺 Channel: {deal['channel']}")
            print(f"   📂 Category: {deal['category']}")
            print(f"   📅 Saved: {deal['created_at']}")
    
    print("\n" + "=" * 80)
    print("✅ View completed")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
