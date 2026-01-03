#!/usr/bin/env python3
"""
Quick Database Setup Checker
=============================
Verifies that the enhanced database schema has been applied correctly.

Usage:
    python check_database.py
"""

from supabase_database import get_supabase_client

def check_database_setup():
    """Check if all new tables and columns exist."""
    
    print("🔍 Checking Database Setup...\n")
    
    try:
        client = get_supabase_client()
        print("✅ Connected to Supabase\n")
        
        checks = []
        
        # Check 1: price_history table
        try:
            result = client.table('price_history').select('*').limit(1).execute()
            checks.append(("price_history table", True))
            print("✅ price_history table exists")
        except Exception as e:
            checks.append(("price_history table", False))
            print(f"❌ price_history table missing: {e}")
        
        # Check 2: deal_sources table
        try:
            result = client.table('deal_sources').select('*').limit(1).execute()
            checks.append(("deal_sources table", True))
            print("✅ deal_sources table exists")
        except Exception as e:
            checks.append(("deal_sources table", False))
            print(f"❌ deal_sources table missing: {e}")
        
        # Check 3: product_urls table
        try:
            result = client.table('product_urls').select('*').limit(1).execute()
            checks.append(("product_urls table", True))
            print("✅ product_urls table exists")
        except Exception as e:
            checks.append(("product_urls table", False))
            print(f"❌ product_urls table missing: {e}")
        
        # Check 4: intelligence_stats table
        try:
            result = client.table('intelligence_stats').select('*').limit(1).execute()
            checks.append(("intelligence_stats table", True))
            print("✅ intelligence_stats table exists")
        except Exception as e:
            checks.append(("intelligence_stats table", False))
            print(f"❌ intelligence_stats table missing: {e}")
        
        # Check 5: Enhanced deals table columns
        try:
            result = client.table('deals').select('deal_score, stock_status, final_effective_price').limit(1).execute()
            checks.append(("deals table enhanced", True))
            print("✅ deals table has new columns")
        except Exception as e:
            checks.append(("deals table enhanced", False))
            print(f"❌ deals table missing new columns: {e}")
        
        # Check 6: Views (try to access one)
        try:
            # Views are accessed like tables in Supabase
            result = client.table('v_top_deals').select('*').limit(1).execute()
            checks.append(("views created", True))
            print("✅ Database views exist")
        except Exception as e:
            checks.append(("views created", False))
            print(f"⚠️  Views might not be accessible via Supabase client (this is OK)")
        
        # Summary
        print("\n" + "="*60)
        passed = sum(1 for _, status in checks if status)
        total = len(checks)
        
        if passed == total:
            print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
            print("\n🎉 Your database is ready for the Intelligence Agent!")
            print("\nNext steps:")
            print("  python intelligence_agent.py        # Run demo")
            print("  python official_deal_monitor.py     # Monitor deals")
        elif passed >= 4:  # At least core tables
            print(f"⚠️  MOSTLY READY ({passed}/{total} passed)")
            print("\nCore functionality should work. Some advanced features may be limited.")
        else:
            print(f"❌ SETUP INCOMPLETE ({passed}/{total} passed)")
            print("\nPlease run the enhanced_database_schema.sql script:")
            print("  1. Go to Supabase Dashboard → SQL Editor")
            print("  2. Copy contents of enhanced_database_schema.sql")
            print("  3. Paste and Run")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease check your Supabase credentials:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")


if __name__ == '__main__':
    check_database_setup()
