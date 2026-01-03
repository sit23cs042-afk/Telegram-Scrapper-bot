"""View recent deals with seller information"""
from supabase_database import get_supabase_client
import json

client = get_supabase_client()
result = client.table('deals').select('id,title,seller_name,seller_rating,is_fulfilled_by_platform,seller_info').order('id', desc=True).limit(5).execute()

print('🔍 Recent Deals with Seller Info:')
print('=' * 70)

for i, deal in enumerate(result.data, 1):
    print(f"\n{i}. {deal['title'][:60]}...")
    print(f"   Seller: {deal.get('seller_name', 'Not extracted')}")
    print(f"   Platform Fulfilled: {'Yes' if deal.get('is_fulfilled_by_platform') else 'No'}")
    if deal.get('seller_info'):
        print(f"   Seller Details: {json.dumps(deal['seller_info'], indent=6)}")
