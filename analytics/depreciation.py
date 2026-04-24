"""
Depreciation curve calculations
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_engine, Listing
from sqlalchemy.orm import sessionmaker

class DepreciationAnalyzer:
    """Calculate depreciation curves for vehicles"""
    
    # Estimated MSRP lookup (simplified)
    MSRP_ESTIMATES = {
        ('Tesla', 'Model 3'): {2021: 39990, 2022: 42990, 2023: 45990},
        ('Tesla', 'Model Y'): {2021: 49990, 2022: 52990, 2023: 54990},
        ('Ford', 'Mustang Mach-E'): {2021: 42995, 2022: 45995, 2023: 48995},
        ('BMW', 'i4'): {2022: 52395, 2023: 53395},
        ('Hyundai', 'Ioniq 5'): {2022: 39950, 2023: 41950},
        ('Kia', 'EV6'): {2022: 40600, 2023: 42600},
    }
    
    def __init__(self):
        self.engine = get_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    def get_msrp(self, brand: str, model: str, year: int) -> float:
        """Get estimated MSRP for a vehicle"""
        brand_models = self.MSRP_ESTIMATES.get((brand, model), {})
        return brand_models.get(year, 0)
    
    def calculate_depreciation(self, brand: str = None, model: str = None):
        """Calculate depreciation for specific or all vehicles"""
        session = self.Session()
        
        query = session.query(Listing)
        if brand:
            query = query.filter(Listing.brand == brand)
        if model:
            query = query.filter(Listing.model == model)
        
        listings = query.all()
        session.close()
        
        if not listings:
            return pd.DataFrame()
        
        data = []
        for listing in listings:
            msrp = self.get_msrp(listing.brand, listing.model, listing.year)
            if msrp > 0 and listing.price > 0:
                depreciation_pct = ((msrp - listing.price) / msrp) * 100
                data.append({
                    'brand': listing.brand,
                    'model': listing.model,
                    'year': listing.year,
                    'msrp': msrp,
                    'current_price': listing.price,
                    'depreciation_percent': round(depreciation_pct, 2),
                    'sample_size': 1
                })
        
        # Group by brand, model, year
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.groupby(['brand', 'model', 'year']).agg({
                'msrp': 'first',
                'current_price': 'mean',
                'depreciation_percent': 'mean',
                'sample_size': 'count'
            }).reset_index()
        
        return df
    
    def get_depreciation_report(self) -> str:
        """Generate depreciation summary report"""
        df = self.calculate_depreciation()
        
        if df.empty:
            return "No depreciation data available"
        
        report = "=" * 60 + "\n"
        report += "DEPRECIATION ANALYSIS REPORT\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        # Best resale value (lowest depreciation)
        report += "🔹 BEST RESALE VALUE (Lowest Depreciation):\n"
        best = df.nsmallest(5, 'depreciation_percent')
        for _, row in best.iterrows():
            report += f"  • {row['year']} {row['brand']} {row['model']}: {row['depreciation_percent']:.1f}% depreciation\n"
        
        report += "\n🔸 WORST RESALE VALUE (Highest Depreciation):\n"
        worst = df.nlargest(5, 'depreciation_percent')
        for _, row in worst.iterrows():
            report += f"  • {row['year']} {row['brand']} {row['model']}: {row['depreciation_percent']:.1f}% depreciation\n"
        
        return report


if __name__ == "__main__":
    analyzer = DepreciationAnalyzer()
    print(analyzer.get_depreciation_report())