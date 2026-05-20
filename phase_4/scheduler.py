import os
import sys
import time
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Groww-Scheduler")

def update_pipeline():
    """
    Executes the full pipeline:
    1. Scrapes latest data from Groww (Phase 1)
    2. Runs the ingestion script to chunk and update ChromaDB (Phase 2)
    """
    logger.info("Starting scheduled update pipeline...")
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    # 1. Run Scraper
    logger.info("Running Scraper (Phase 1)...")
    scraper_script = os.path.join(project_root, "phase_1", "scraper.py")
    try:
        subprocess.run([sys.executable, scraper_script], check=True)
        logger.info("Scraping completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Scraping failed: {e}")
        return # Abort ingestion if scraping fails

    # 2. Run Ingestion (Vector DB Update)
    logger.info("Running Vector DB Ingestion (Phase 2)...")
    ingest_script = os.path.join(project_root, "phase_2", "ingest.py")
    try:
        subprocess.run([sys.executable, ingest_script], check=True)
        logger.info("Vector DB Ingestion completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ingestion failed: {e}")
        return

    logger.info("Scheduled update pipeline finished successfully!")

if __name__ == "__main__":
    logger.info("Starting Groww RAG Scheduler...")
    
    # Run once immediately on startup
    update_pipeline()
    
    # Setup scheduler with Asia/Kolkata (IST) timezone
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    
    # Schedule to run every day at 9:00 AM IST
    # Mutual fund NAVs and data usually update at the end of the trading day,
    # so morning is a safe time to grab fresh data.
    scheduler.add_job(update_pipeline, 'cron', hour=9, minute=0)
    
    scheduler.start()
    logger.info("Scheduler is running in the background. Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shutdown gracefully.")
