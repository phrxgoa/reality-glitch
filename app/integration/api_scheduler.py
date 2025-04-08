import time
import logging
import sys
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Import the function from your sync script
from integration.sync_apis import SyncApis

# Configure logging to be silent unless critical errors
logging.basicConfig(
    level=logging.ERROR,  # Only show ERROR and above
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # Add a null handler to prevent console output
        logging.NullHandler()
    ]
)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # Schedule the perform_sync function to run every 10 minutes
    sync_apis = SyncApis()
    scheduler.add_job(sync_apis.sync_all, 'interval', minutes=10, id='data_sync_job', replace_existing=True)

    # No logging here, should be silent
    try:
        # Start the scheduler (this blocks execution)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # Silent shutdown
        scheduler.shutdown()