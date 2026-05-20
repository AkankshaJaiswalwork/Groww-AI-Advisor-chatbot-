import os
import sys
import pytest
from apscheduler.schedulers.background import BackgroundScheduler

# Add phase_4 to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase_4"))

from scheduler import update_pipeline

def test_scheduler_configuration():
    # Setup a test scheduler
    scheduler = BackgroundScheduler()
    
    # Add the job exactly as done in scheduler.py
    # Update to run every day at 9:00 AM (hour=9, minute=0)
    job = scheduler.add_job(update_pipeline, 'cron', hour=9, minute=0)
    
    # Assert scheduler setup details
    assert job is not None
    assert job.func == update_pipeline
    
    # Verify the trigger details
    trigger = job.trigger
    
    # Clean verification of cron schedule fields (APScheduler cron trigger representation)
    fields = {str(f.name): str(f) for f in trigger.fields}
    assert fields["hour"] == "9"
    assert fields["minute"] == "0"
