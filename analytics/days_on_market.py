"""
Days on market analysis
"""

import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_engine, Listing
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

class DaysOnMarketAnalyzer:
    """Analyze listing duration"""
    
    def __init__(self):
        self.engine = get_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    def calculate_days_on_market(self, days_back: int = 30) -> pd.DataFrame:
        """Calculate average days on market"""
        session = self.Session()
        
        cutoff_date = datetime.now().date() - timedelta(days=days_back)
        
        query = session.query(
            Listing.brand,
            Listing.model,
            func.avg(func.julianday(datetime.now()) - func.julianday(Listing.listing_date)).label('avg_days')
        ).filter(
            Listing.listing_date >= cutoff_date
        ).group_by(
            Listing.brand, Listing.model
        ).all()
        
        session.close()
        
        if not query:
            return pd.DataFrame()
        
        data = []
        for brand, model, avg_days in query:
            data.append({
                'brand': brand,
                'model': model,
                'avg_days_on_market': round(avg_days, 1) if avg_days else 0
            })
        
        return pd.DataFrame(data)
    
    def get_report(self) -> str:
        """Generate days on market report"""
        df = self.calculate_days_on_market()
        
        if df.empty:
            return "No data available"
        
        df = df.sort_values('avg_days_on_market', ascending=False)
        
        report = "=" * 60 + "\n"
        report += "DAYS ON MARKET ANALYSIS\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        report += "🔸 SLOWEST MOVING (Longest on market):\n"
        for _, row in df.head(5).iterrows():
            report += f"  • {row['brand']} {row['model']}: {row['avg_days_on_market']} days\n"
        
        report += "\n🔹 FASTEST MOVING (Shortest on market):\n"
        for _, row in df.tail(5).iterrows():
            report += f"  • {row['brand']} {row['model']}: {row['avg_days_on_market']} days\n"
        
        return report


if __name__ == "__main__":
    analyzer = DaysOnMarketAnalyzer()
    print(analyzer.get_report())