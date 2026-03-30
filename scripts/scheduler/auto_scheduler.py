"""
Auto-Run Scheduler for AI Engine
Runs MasterController.run_full_pipeline() every 10 minutes
Stores results in data/live/latest_run.json
Logs every run with timestamp
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Thread, Event

from core.master_controller import MasterController

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/live/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutoScheduler')

# Constants
INTERVAL_MINUTES = 10
MAX_RETRIES = 3
LIVE_DATA_PATH = Path('data/live/latest_run.json')
SAMPLE_LEADS = [
    {
        "name": "Auto Lead 1",
        "company": "TechCorp",
        "industry": "Technology",
        "budget": 50000,
        "location": "Dubai"
    },
    {
        "name": "Auto Lead 2",
        "company": "FinanceInc",
        "industry": "Finance",
        "budget": 100000,
        "location": "London"
    }
]

class AutoScheduler:
    """
    Auto-running scheduler for AI Engine pipeline
    Runs every 10 minutes with retry logic
    """
    
    def __init__(self):
        self.controller = MasterController()
        self.stop_event = Event()
        self.last_run = None
        self.run_count = 0
        self.error_count = 0
        
    def run_pipeline_with_retry(self):
        """
        Run pipeline with retry logic
        Returns: (success: bool, result: dict)
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"Running pipeline (attempt {attempt}/{MAX_RETRIES})...")
                
                # Run full pipeline
                result = self.controller.run_full_pipeline(
                    {"leads": SAMPLE_LEADS},
                    role="admin"
                )
                
                # Check for errors in result
                if "error" in result:
                    raise Exception(result["error"])
                
                logger.info(f"Pipeline completed successfully on attempt {attempt}")
                return True, result
                
            except Exception as e:
                logger.error(f"Pipeline failed on attempt {attempt}: {str(e)}")
                if attempt < MAX_RETRIES:
                    wait_time = attempt * 2  # Exponential backoff
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed")
                    return False, {"error": str(e), "attempts": attempt}
        
        return False, {"error": "Unknown error"}
    
    def save_live_data(self, result: dict):
        """
        Save results to data/live/latest_run.json
        """
        try:
            # Ensure directory exists
            LIVE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare live data with metadata
            live_data = {
                "timestamp": datetime.now().isoformat(),
                "run_id": self.run_count,
                "status": "success",
                "data": result
            }
            
            # Write to file
            with open(LIVE_DATA_PATH, 'w') as f:
                json.dump(live_data, f, indent=2, default=str)
            
            logger.info(f"Live data saved to {LIVE_DATA_PATH}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save live data: {str(e)}")
            return False
    
    def run_single_cycle(self):
        """
        Execute one cycle of the scheduler
        """
        self.run_count += 1
        start_time = time.time()
        
        logger.info(f"=== Starting cycle #{self.run_count} ===")
        
        # Run pipeline with retry
        success, result = self.run_pipeline_with_retry()
        
        # Save results
        if success:
            self.save_live_data(result)
            self.last_run = datetime.now()
            duration = time.time() - start_time
            logger.info(f"Cycle #{self.run_count} completed in {duration:.2f}s")
        else:
            self.error_count += 1
            # Save error state
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "run_id": self.run_count,
                "status": "error",
                "error": result.get("error", "Unknown error"),
                "attempts": result.get("attempts", 0)
            }
            try:
                with open(LIVE_DATA_PATH, 'w') as f:
                    json.dump(error_data, f, indent=2)
            except:
                pass
            logger.error(f"Cycle #{self.run_count} failed after all retries")
        
        logger.info(f"=== Cycle #{self.run_count} finished ===")
    
    def start(self):
        """
        Start the scheduler in a background thread
        """
        logger.info("Auto-Scheduler starting...")
        logger.info(f"Interval: {INTERVAL_MINUTES} minutes")
        logger.info(f"Max retries: {MAX_RETRIES}")
        logger.info(f"Live data path: {LIVE_DATA_PATH}")
        
        def scheduler_loop():
            while not self.stop_event.is_set():
                self.run_single_cycle()
                
                # Wait for next interval
                logger.info(f"Waiting {INTERVAL_MINUTES} minutes until next run...")
                
                # Check stop event every second
                for _ in range(INTERVAL_MINUTES * 60):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
        
        # Start in background thread
        self.thread = Thread(target=scheduler_loop, daemon=True)
        self.thread.start()
        logger.info("Auto-Scheduler started in background thread")
        
    def stop(self):
        """
        Stop the scheduler
        """
        logger.info("Stopping Auto-Scheduler...")
        self.stop_event.set()
        if hasattr(self, 'thread'):
            self.thread.join(timeout=5)
        logger.info("Auto-Scheduler stopped")
    
    def get_status(self):
        """
        Get current scheduler status
        """
        return {
            "running": not self.stop_event.is_set(),
            "run_count": self.run_count,
            "error_count": self.error_count,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "interval_minutes": INTERVAL_MINUTES,
            "max_retries": MAX_RETRIES
        }

# Global scheduler instance
_scheduler = None

def start_scheduler():
    """
    Start the global scheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = AutoScheduler()
        _scheduler.start()
    return _scheduler

def stop_scheduler():
    """
    Stop the global scheduler instance
    """
    global _scheduler
    if _scheduler is not None:
        _scheduler.stop()
        _scheduler = None

def get_scheduler_status():
    """
    Get scheduler status
    """
    global _scheduler
    if _scheduler is not None:
        return _scheduler.get_status()
    return {"running": False, "message": "Scheduler not started"}

if __name__ == "__main__":
    # Run scheduler directly
    scheduler = AutoScheduler()
    try:
        scheduler.start()
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down scheduler...")
        scheduler.stop()
