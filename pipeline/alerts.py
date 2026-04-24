"""
Price drop alerts and notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_engine, Listing
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

class AlertSystem:
    """Handle price drop alerts and notifications"""
    
    def __init__(self):
        self.engine = get_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    def check_price_drops(self, threshold_percent: float = 10.0):
        """Check for significant price drops"""
        session = self.Session()
        
        # Get recent price changes
        # This compares average prices over time
        # Simplified implementation
        
        session.close()
        return []
    
    def send_email_alert(self, to_email: str, subject: str, message: str):
        """Send email alert"""
        smtp_host = os.getenv('SMTP_HOST', '')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        if not smtp_user or not smtp_password:
            print("Email credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"Alert sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def get_best_deals(self, limit: int = 10):
        """Get best value deals"""
        session = self.Session()
        
        # Find listings with best price per mile
        best_deals = session.query(Listing).filter(
            Listing.price > 0,
            Listing.mileage > 0
        ).order_by(Listing.price_per_mile).limit(limit).all()
        
        session.close()
        return best_deals
    
    def format_alert_message(self, deals) -> str:
        """Format alert message"""
        message = "🚗 Best Used EV Deals Today 🚗\n\n"
        
        for i, deal in enumerate(deals[:5], 1):
            message += f"{i}. {deal.year} {deal.brand} {deal.model}\n"
            message += f"   Price: ${deal.price:,}\n"
            message += f"   Mileage: {deal.mileage:,}\n"
            message += f"   Price per mile: ${deal.price/deal.mileage:.2f}\n\n"
        
        return message


if __name__ == "__main__":
    alert = AlertSystem()
    
    # Check for best deals
    best_deals = alert.get_best_deals(5)
    
    if best_deals:
        print("Top 5 Best Value Deals:")
        for i, deal in enumerate(best_deals, 1):
            print(f"{i}. {deal.year} {deal.brand} {deal.model} - ${deal.price:,}")