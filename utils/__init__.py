"""Utils package for daily deals scraping"""

from .helpers import (
    get_random_user_agent,
    fetch_page,
    extract_price,
    calculate_discount_percentage,
    clean_text,
    validate_url,
    format_deal_data,
    batch_items,
    RateLimiter,
    rate_limiter
)

__all__ = [
    'get_random_user_agent',
    'fetch_page',
    'extract_price',
    'calculate_discount_percentage',
    'clean_text',
    'validate_url',
    'format_deal_data',
    'batch_items',
    'RateLimiter',
    'rate_limiter'
]
