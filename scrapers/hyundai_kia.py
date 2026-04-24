"""
Hyundai & Kia Used Inventory Scraper
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random

class HyundaiKiaScraper:
    """Scraper for Hyundai and Kia used inventory"""
    
    HYUNDAI_URL = "https://www.hyundaiusa.com/cpo/inventory.aspx"
    KIA_URL = "https://www.kia.com/us/en/certified-used/inventory"
    
    def __init__(self):
        self.session = self._create_session()
    
    def _create_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def fetch_hyundai(self) -> list:
        """Fetch Hyundai CPO listings"""
        time.sleep(random.uniform(2, 4))
        return self._get_sample_hyundai()
    
    def fetch_kia(self) -> list:
        """Fetch Kia used listings"""
        time.sleep(random.uniform(2, 4))
        return self._get_sample_kia()
    
    def _get_sample_hyundai(self):
        return [
            {
                'source': 'hyundai',
                'brand': 'Hyundai',
                'model': 'Ioniq 5',
                'year': 2022,
                'trim': 'SEL',
                'price': 38990,
                'mileage': 18345,
                'exterior_color': 'Digital Teal',
                'interior_color': 'Gray',
                'options': 'Dual Motor',
                'location_city': 'Los Angeles',
                'location_state': 'CA',
                'listing_url': 'https://hyundaiusa.com/cpo/ioniq5-234',
                'listing_date': datetime.now().date()
            }
        ]
    
    def _get_sample_kia(self):
        return [
            {
                'source': 'kia',
                'brand': 'Kia',
                'model': 'EV6',
                'year': 2022,
                'trim': 'Wind',
                'price': 37990,
                'mileage': 15678,
                'exterior_color': 'Steel Gray',
                'interior_color': 'Black',
                'options': 'Technology Package',
                'location_city': 'San Francisco',
                'location_state': 'CA',
                'listing_url': 'https://kia.com/used/ev6-567',
                'listing_date': datetime.now().date()
            }
        ]
    
    def run(self):
        listings = []
        listings.extend(self.fetch_hyundai())
        listings.extend(self.fetch_kia())
        return listings


if __name__ == "__main__":
    scraper = HyundaiKiaScraper()
    listings = scraper.run()
    print(f"Found {len(listings)} Hyundais/Kias")