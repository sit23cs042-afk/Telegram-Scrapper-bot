"""
Category-wise Deal Viewer
=========================
View and manage deals organized by categories.

Features:
- View deals by specific category
- List all categories with deal counts
- View active deals only (excludes expired offers)
- Cleanup expired deals

Author: AI Assistant
Date: December 2025
"""

import sys
from datetime import datetime
from typing import List, Dict
from supabase_database import (
    init_database,
    get_deals_by_category_supabase,
    get_all_categories,
    cleanup_expired_deals,
    get_active_deals
)


def print_separator(char='=', length=80):
    """Print a separator line."""
    print(char * length)


def display_categories():
    """Display all categories with deal counts."""
    print_separator()
    print("📂 ALL CATEGORIES")
    print_separator()
    print()
    
    categories = get_all_categories()
    
    if not categories:
        print("❌ No active categories found")
        return
    
    total_deals = sum(cat['count'] for cat in categories)
    
    print(f"Total Active Deals: {total_deals}")
    print()
    print(f"{'Category':<20} {'Count':<10}")
    print("-" * 35)
    
    for cat_info in categories:
        category = cat_info['category'].title()
        count = cat_info['count']
        print(f"{category:<20} {count:<10}")
    
    print()


def display_deals_by_category(category: str, limit: int = 20):
    """Display deals from a specific category."""
    print_separator()
    print(f"🏷️  {category.upper()} DEALS")
    print_separator()
    print()
    
    deals = get_deals_by_category_supabase(category, limit)
    
    if not deals:
        print(f"❌ No active deals found in category: {category}")
        return
    
    print(f"Found {len(deals)} active deal(s):")
    print()
    
    for idx, deal in enumerate(deals, 1):
        print(f"{'='*80}")
        print(f"Deal #{idx}")
        print(f"{'='*80}")
        print(f"📦 Title: {deal.get('title', 'N/A')}")
        print(f"💰 Price: ₹{deal.get('verified_price', 'N/A')}")
        
        if deal.get('verified_mrp'):
            print(f"🏷️  MRP: ₹{deal.get('verified_mrp')}")
        
        if deal.get('verified_discount'):
            print(f"🎯 Discount: {deal.get('verified_discount')}%")
        
        if deal.get('rating'):
            print(f"⭐ Rating: {deal.get('rating')}/5")
        
        print(f"🔗 Link: {deal.get('link', 'N/A')}")
        
        if deal.get('offer_end_date'):
            print(f"⏰ Expires: {deal.get('offer_end_date')}")
        
        if deal.get('timestamp'):
            print(f"📅 Added: {deal.get('timestamp')}")
        
        print()


def cleanup_expired():
    """Cleanup expired deals."""
    print_separator()
    print("🧹 CLEANUP EXPIRED DEALS")
    print_separator()
    print()
    
    count = cleanup_expired_deals()
    
    if count > 0:
        print(f"✅ Successfully removed {count} expired deal(s)")
    else:
        print("✅ No expired deals to cleanup")
    
    print()


def display_active_deals(limit: int = 20):
    """Display all active deals across categories."""
    print_separator()
    print("📋 ALL ACTIVE DEALS")
    print_separator()
    print()
    
    deals = get_active_deals(limit)
    
    if not deals:
        print("❌ No active deals found")
        return
    
    print(f"Found {len(deals)} active deal(s):")
    print()
    
    # Group by category
    deals_by_cat = {}
    for deal in deals:
        cat = deal.get('category', 'other')
        if cat not in deals_by_cat:
            deals_by_cat[cat] = []
        deals_by_cat[cat].append(deal)
    
    for category, cat_deals in sorted(deals_by_cat.items()):
        print(f"\n{'='*80}")
        print(f"🏷️  {category.upper()} ({len(cat_deals)} deals)")
        print(f"{'='*80}\n")
        
        for idx, deal in enumerate(cat_deals[:5], 1):  # Show top 5 per category
            print(f"  {idx}. {deal.get('title', 'N/A')[:60]}")
            print(f"     💰 ₹{deal.get('verified_price')} ", end='')
            
            if deal.get('verified_discount'):
                print(f"({deal.get('verified_discount')}% off)", end='')
            
            if deal.get('rating'):
                print(f" ⭐ {deal.get('rating')}", end='')
            
            print()
            print(f"     🔗 {deal.get('link', 'N/A')[:70]}")
            print()


def print_menu():
    """Print the menu options."""
    print_separator()
    print("🛍️  CATEGORY-WISE DEAL VIEWER")
    print_separator()
    print()
    print("Options:")
    print("  1. View all categories")
    print("  2. View deals by category")
    print("  3. View all active deals")
    print("  4. Cleanup expired deals")
    print("  5. Exit")
    print()


def main():
    """Main function."""
    print()
    print_separator('=')
    print("INITIALIZING DATABASE...")
    print_separator('=')
    print()
    
    # Initialize database
    try:
        init_database()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)
    
    print()
    
    # Available categories
    available_categories = [
        'electronics', 'fashion', 'home', 'beauty', 
        'books', 'grocery', 'sports', 'other'
    ]
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            print()
            
            if choice == '1':
                display_categories()
                
            elif choice == '2':
                print("Available categories:")
                for cat in available_categories:
                    print(f"  - {cat}")
                print()
                
                category = input("Enter category name: ").strip().lower()
                
                if category not in available_categories:
                    print(f"⚠️  Warning: '{category}' is not a standard category")
                
                limit = input("Number of deals to show (default 20): ").strip()
                limit = int(limit) if limit.isdigit() else 20
                
                print()
                display_deals_by_category(category, limit)
                
            elif choice == '3':
                limit = input("Number of deals to show (default 20): ").strip()
                limit = int(limit) if limit.isdigit() else 20
                
                print()
                display_active_deals(limit)
                
            elif choice == '4':
                confirm = input("Are you sure you want to cleanup expired deals? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    print()
                    cleanup_expired()
                else:
                    print("❌ Cleanup cancelled")
                    print()
                
            elif choice == '5':
                print("👋 Goodbye!")
                print()
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                print()
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            print()
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()


if __name__ == "__main__":
    main()
