"""
Geographic price variation analysis
"""

import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_engine, Listing
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

class GeographicAnalyzer:
    """Analyze price variations by location"""
    
    def __init__(self):
        self.engine = get_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    def get_price_by_state(self, brand: str = None) -> pd.DataFrame:
        """Get average price by state"""
        session = self.Session()
        
        query = session.query(
            Listing.location_state,
            func.avg(Listing.price).label('avg_price'),
            func.count(Listing.id).label('listing_count')
        ).filter(
            Listing.location_state != '',
            Listing.price > 0
        )
        
        if brand:
            query = query.filter(Listing.brand == brand)
        
        results = query.group_by(Listing.location_state).all()
        session.close()
        
        if not results:
            return pd.DataFrame()
        
        data = []
        for state, avg_price, count in results:
            if count >= 3:  # Minimum sample size
                data.append({
                    'state': state,
                    'avg_price': round(avg_price, 0),
                    'listings': count
                })
        
        return pd.DataFrame(data)
    
    def get_cheapest_states(self, brand: str = None, limit: int = 5) -> pd.DataFrame:
        """Get cheapest states for a brand"""
        df = self.get_price_by_state(brand)
        
        if df.empty:
            return pd.DataFrame()
        
        return df.nsmallest(limit, 'avg_price')
    
    def get_most_expensive_states(self, brand: str = None, limit: int = 5) -> pd.DataFrame:
        """Get most expensive states for a brand"""
        df = self.get_price_by_state(brand)
        
        if df.empty:
            return pd.DataFrame()
        
        return df.nlargest(limit, 'avg_price')
    
    def get_report(self, brand: str = "Tesla") -> str:
        """Generate geographic price report"""
        cheapest = self.get_cheapest_states(brand, 5)
        expensive = self.get_most_expensive_states(brand, 5)
        
        report = "=" * 60 + "\n"
        report += f"GEOGRAPHIC PRICE ANALYSIS - {brand}\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        report += "🔹 CHEAPEST STATES TO BUY:\n"
        for _, row in cheapest.iterrows():
            report += f"  • {row['state']}: ${row['avg_price']:,.0f} (avg, {row['listings']} listings)\n"
        
        report += "\n🔸 MOST EXPENSIVE STATES:\n"
        for _, row in expensive.iterrows():
            report += f"  • {row['state']}: ${row['avg_price']:,.0f} (avg, {row['listings']} listings)\n"
        
        report += f"\n💡 Savings Potential: Up to ${expensive['avg_price'].max() - cheapest['avg_price'].min():,.0f}\n"
        
        return report


if __name__ == "__main__":
    analyzer = GeographicAnalyzer()
    print(analyzer.get_report("Tesla"))