"""
Scheduler for daily/weekly pipeline runs
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.etl import run_etl

def scheduled_job():
    """Job to run ETL pipeline"""
    print(f"[{datetime.now()}] Running scheduled ETL pipeline...")
    try:
        run_etl()
        print(f"[{datetime.now()}] ETL pipeline completed successfully")
    except Exception as e:
        print(f"[{datetime.now()}] ETL pipeline failed: {e}")

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Schedule daily at 2 AM
    scheduler.add_job(
        func=scheduled_job,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_etl',
        name='Run ETL pipeline daily at 2 AM',
        replace_existing=True
    )
    
    # Schedule weekly on Sunday at 3 AM (full refresh)
    scheduler.add_job(
        func=scheduled_job,
        trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
        id='weekly_refresh',
        name='Weekly full refresh',
        replace_existing=True
    )
    
    scheduler.start()
    print("Scheduler started. Jobs scheduled:")
    print("  - Daily ETL: 2:00 AM")
    print("  - Weekly refresh: Sunday 3:00 AM")
    
    return scheduler

if __name__ == "__main__":
    scheduler = start_scheduler()
    
    try:
        # Keep the script running
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        scheduler.shutdown()