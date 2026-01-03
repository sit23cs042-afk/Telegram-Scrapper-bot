"""Database package for daily deals management"""

from .supabase_client import DailyDealsDB, get_db_client

__all__ = ['DailyDealsDB', 'get_db_client']
