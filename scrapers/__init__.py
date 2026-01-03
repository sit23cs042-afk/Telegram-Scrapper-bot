"""Scrapers package for daily deals"""

from .amazon import scrape_amazon_deals
from .flipkart import scrape_flipkart_deals
from .myntra import scrape_myntra_deals
from .ajio import scrape_ajio_deals
from .meesho import scrape_meesho_deals
from .tata_cliq import scrape_tata_cliq_deals
from .reliance_digital import scrape_reliance_digital_deals

__all__ = [
    'scrape_amazon_deals',
    'scrape_flipkart_deals',
    'scrape_myntra_deals',
    'scrape_ajio_deals',
    'scrape_meesho_deals',
    'scrape_tata_cliq_deals',
    'scrape_reliance_digital_deals'
]
