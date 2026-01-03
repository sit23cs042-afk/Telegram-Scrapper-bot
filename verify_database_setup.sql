-- ============================================================================
-- Verification Script - Check Database Setup
-- ============================================================================
-- Run this in Supabase SQL Editor to verify all components are installed
-- ============================================================================

-- 1. Check if all new tables exist
SELECT 
    'Tables Check' as check_type,
    CASE 
        WHEN COUNT(*) = 4 THEN '✅ All 4 tables exist'
        ELSE '❌ Missing tables: ' || (4 - COUNT(*))::text
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('price_history', 'deal_sources', 'product_urls', 'intelligence_stats');

-- 2. Check if all views exist
SELECT 
    'Views Check' as check_type,
    CASE 
        WHEN COUNT(*) = 5 THEN '✅ All 5 views exist'
        ELSE '❌ Missing views: ' || (5 - COUNT(*))::text
    END as status
FROM information_schema.views 
WHERE table_schema = 'public' 
AND table_name IN ('v_top_deals', 'v_historical_low_deals', 'v_high_value_deals', 'v_price_history_summary', 'v_daily_stats');

-- 3. Check if deals table has new columns
SELECT 
    'Deals Table Enhancement' as check_type,
    CASE 
        WHEN COUNT(*) >= 10 THEN '✅ New columns added'
        ELSE '❌ Some columns missing: ' || COUNT(*)::text || '/10+'
    END as status
FROM information_schema.columns 
WHERE table_name = 'deals' 
AND column_name IN (
    'stock_status', 'in_stock', 'stock_message',
    'deal_score', 'deal_grade', 'recommendation',
    'final_effective_price', 'total_savings',
    'is_historical_low', 'is_fake_discount'
);

-- 4. Check if functions exist
SELECT 
    'Functions Check' as check_type,
    CASE 
        WHEN COUNT(*) >= 2 THEN '✅ Functions created'
        ELSE '❌ Functions missing'
    END as status
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.proname IN ('update_product_url_mapping', 'update_daily_stats');

-- 5. Check indexes on price_history
SELECT 
    'Indexes Check' as check_type,
    CASE 
        WHEN COUNT(*) >= 3 THEN '✅ Indexes created'
        ELSE '❌ Some indexes missing'
    END as status
FROM pg_indexes
WHERE tablename = 'price_history'
AND indexname LIKE 'idx_%';

-- 6. Detailed table list
SELECT 
    'Detailed Table List' as info_type,
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('deals', 'price_history', 'deal_sources', 'product_urls', 'intelligence_stats')
ORDER BY table_name;

-- 7. Row Level Security check
SELECT 
    'RLS Check' as check_type,
    tablename,
    CASE 
        WHEN rowsecurity THEN '✅ Enabled'
        ELSE '❌ Disabled'
    END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('price_history', 'deal_sources', 'product_urls', 'intelligence_stats')
ORDER BY tablename;

-- ============================================================================
-- Sample Test Queries
-- ============================================================================

-- Test 1: Count existing deals
SELECT 'Existing Deals' as metric, COUNT(*) as count FROM deals;

-- Test 2: Check if price_history is ready for data
SELECT 'Price History Ready' as status, 
    CASE 
        WHEN EXISTS (SELECT 1 FROM price_history LIMIT 1) 
        THEN 'Has data (' || (SELECT COUNT(*)::text FROM price_history) || ' records)'
        ELSE 'Empty (ready for new data)'
    END as info;

-- Test 3: Check intelligence_stats
SELECT 'Intelligence Stats' as status,
    CASE 
        WHEN EXISTS (SELECT 1 FROM intelligence_stats LIMIT 1)
        THEN 'Has data (' || (SELECT COUNT(*)::text FROM intelligence_stats) || ' days)'
        ELSE 'Empty (will populate automatically)'
    END as info;

-- ============================================================================
-- Summary
-- ============================================================================

SELECT '
════════════════════════════════════════════════════════════════
                    VERIFICATION SUMMARY
════════════════════════════════════════════════════════════════

Run the queries above to check:
✅ Tables: 4 new tables (price_history, deal_sources, product_urls, intelligence_stats)
✅ Views: 5 analytics views
✅ Columns: 30+ new columns in deals table
✅ Functions: 2 utility functions
✅ Indexes: Multiple indexes for performance
✅ RLS: Row Level Security enabled

If all checks show ✅, your database is ready!

Next steps:
1. python intelligence_agent.py (test the system)
2. python official_deal_monitor.py (monitor deal pages)

════════════════════════════════════════════════════════════════
' as summary;
