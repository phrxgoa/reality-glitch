import time
import logging
import sys
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Import the function from your sync script
from integration.sync_apis import SyncApis

# Configure logging for the scheduler itself (optional)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # Schedule the perform_sync function to run every 10 minutes
    sync_apis = SyncApis()
    scheduler.add_job(sync_apis.sync_all, 'interval', minutes=10, id='data_sync_job', replace_existing=True)

    logging.info("\n#### Starting scheduler. Press Ctrl+C to exit. ####\n")

    try:
        # Start the scheduler (this blocks execution)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # Handle graceful shutdown
        logging.info("Scheduler stopped.")
        scheduler.shutdown()