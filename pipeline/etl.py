"""
ETL Pipeline - Extract, Transform, Load
"""

import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import scrapers - using correct class names
from scrapers.tesla_api import TeslaScraper
from scrapers.ford import FordScraper
from scrapers.bmw import BMWScraper
from scrapers.hyundai_kia import HyundaiKiaScraper
from scrapers.toyota import ToyotaScraper
from scrapers.mercedes import MercedesScraper
from scrapers.volkswagen import VolkswagenScraper
from scrapers.polestar import PolestarScraper
from database.models import get_engine, Listing, Base
from sqlalchemy.orm import sessionmaker

def run_all_scrapers() -> list:
    """Run all scrapers and collect data"""
    
    all_listings = []
    
    print("=" * 50)
    print("Running Tesla Scraper...")
    try:
        tesla = TeslaScraper()
        tesla_listings = tesla.run()
        all_listings.extend(tesla_listings)
        print(f"  Found {len(tesla_listings)} Teslas")
    except Exception as e:
        print(f"  Tesla scraper error: {e}")
    
    print("Running Ford Scraper...")
    try:
        ford = FordScraper()
        ford_listings = ford.run()
        all_listings.extend(ford_listings)
        print(f"  Found {len(ford_listings)} Fords")
    except Exception as e:
        print(f"  Ford scraper error: {e}")
    
    print("Running BMW Scraper...")
    try:
        bmw = BMWScraper()
        bmw_listings = bmw.run()
        all_listings.extend(bmw_listings)
        print(f"  Found {len(bmw_listings)} BMWs")
    except Exception as e:
        print(f"  BMW scraper error: {e}")
    
    print("Running Hyundai/Kia Scraper...")
    try:
        hk = HyundaiKiaScraper()
        hk_listings = hk.run()
        all_listings.extend(hk_listings)
        print(f"  Found {len(hk_listings)} Hyundais/Kias")
    except Exception as e:
        print(f"  Hyundai/Kia scraper error: {e}")
    
    print("Running Toyota Scraper...")
    try:
        toyota = ToyotaScraper()
        toyota_listings = toyota.run()
        all_listings.extend(toyota_listings)
        print(f"  Found {len(toyota_listings)} Toyotas")
    except Exception as e:
        print(f"  Toyota scraper error: {e}")
    
    print("Running Mercedes Scraper...")
    try:
        mercedes = MercedesScraper()
        mercedes_listings = mercedes.run()
        all_listings.extend(mercedes_listings)
        print(f"  Found {len(mercedes_listings)} Mercedes")
    except Exception as e:
        print(f"  Mercedes scraper error: {e}")
    
    print("Running Volkswagen Scraper...")
    try:
        vw = VolkswagenScraper()
        vw_listings = vw.run()
        all_listings.extend(vw_listings)
        print(f"  Found {len(vw_listings)} Volkswagens")
    except Exception as e:
        print(f"  Volkswagen scraper error: {e}")
    
    print("Running Polestar Scraper...")
    try:
        polestar = PolestarScraper()
        polestar_listings = polestar.run()
        all_listings.extend(polestar_listings)
        print(f"  Found {len(polestar_listings)} Polestars")
    except Exception as e:
        print(f"  Polestar scraper error: {e}")
    
    print(f"Total listings collected: {len(all_listings)}")
    return all_listings


def clean_listings(listings: list) -> pd.DataFrame:
    """Clean and transform listings"""
    
    if not listings:
        print("No listings to clean")
        return pd.DataFrame()
    
    df = pd.DataFrame(listings)
    
    # Remove duplicates
    if 'listing_url' in df.columns:
        df = df.drop_duplicates(subset=['listing_url'])
    
    # Clean numeric fields
    if 'price' in df.columns:
        df['price'] = df['price'].fillna(0).astype(int)
    if 'mileage' in df.columns:
        df['mileage'] = df['mileage'].fillna(0).astype(int)
    
    # Filter invalid
    if 'price' in df.columns:
        df = df[df['price'] > 1000]
    if 'mileage' in df.columns:
        df = df[df['mileage'] < 200000]
    if 'year' in df.columns:
        df = df[df['year'] >= 2015]
    
    # Add price per mile
    if 'price' in df.columns and 'mileage' in df.columns:
        df['price_per_mile'] = df.apply(
            lambda row: row['price'] / max(row['mileage'], 1), axis=1
        )
    
    print(f"Cleaned {len(df)} listings")
    return df


def save_to_database(df: pd.DataFrame):
    """Save cleaned data to database"""
    
    if df.empty:
        print("No data to save")
        return
    
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    try:
        # Save to listings table
        df.to_sql('listings', engine, if_exists='append', index=False)
        print(f"Saved {len(df)} listings to database")
    except Exception as e:
        print(f"Error saving to database: {e}")


def run_etl():
    """Main ETL pipeline"""
    
    print("Starting ETL Pipeline...")
    
    # Extract
    raw_listings = run_all_scrapers()
    
    # Transform
    clean_df = clean_listings(raw_listings)
    
    # Load
    save_to_database(clean_df)
    
    print("ETL Pipeline Complete")


if __name__ == "__main__":
    run_etl()