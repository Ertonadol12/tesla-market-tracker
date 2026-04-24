"""
Price per mile efficiency analysis
"""

import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_engine, Listing
from sqlalchemy.orm import sessionmaker

class PricePerMileAnalyzer:
    """Calculate cost efficiency metrics"""
    
    def __init__(self):
        self.engine = get_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    def get_efficiency_data(self, brand: str = None) -> pd.DataFrame:
        """Get price per mile data"""
        session = self.Session()
        
        query = session.query(Listing).filter(
            Listing.price > 0,
            Listing.mileage > 0
        )
        
        if brand:
            query = query.filter(Listing.brand == brand)
        
        listings = query.all()
        session.close()
        
        if not listings:
            return pd.DataFrame()
        
        data = []
        for listing in listings:
            data.append({
                'brand': listing.brand,
                'model': listing.model,
                'year': listing.year,
                'price': listing.price,
                'mileage': listing.mileage,
                'price_per_mile': round(listing.price / listing.mileage, 2)
            })
        
        return pd.DataFrame(data)
    
    def get_best_value_ranking(self, limit: int = 10) -> pd.DataFrame:
        """Get best value rankings by price per mile"""
        df = self.get_efficiency_data()
        
        if df.empty:
            return pd.DataFrame()
        
        # Group by brand and model
        ranking = df.groupby(['brand', 'model', 'year']).agg({
            'price_per_mile': 'mean',
            'price': 'mean',
            'mileage': 'mean'
        }).reset_index()
        
        ranking = ranking.sort_values('price_per_mile').head(limit)
        return ranking
    
    def get_report(self) -> str:
        """Generate price per mile report"""
        ranking = self.get_best_value_ranking(10)
        
        if ranking.empty:
            return "No data available"
        
        report = "=" * 60 + "\n"
        report += "BEST VALUE RANKING (Lowest Price per Mile)\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        for i, row in ranking.iterrows():
            report += f"{i+1}. {row['year']} {row['brand']} {row['model']}\n"
            report += f"   Price per mile: ${row['price_per_mile']:.2f}\n"
            report += f"   Average price: ${row['price']:,.0f}\n"
            report += f"   Average mileage: {row['mileage']:,.0f}\n\n"
        
        return report


if __name__ == "__main__":
    analyzer = PricePerMileAnalyzer()
    print(analyzer.get_report())