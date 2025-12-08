#!/usr/bin/env python3
"""
Scheduler daemon for continuous price checking.

This script runs the price checker on a configurable interval.
The interval is controlled via the CHECK_INTERVAL_SECONDS environment variable.
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from main import main


def get_check_interval() -> int:
    """Get check interval from environment variable."""
    default_interval = 3600  # 1 hour
    interval_str = os.environ.get('CHECK_INTERVAL_SECONDS', str(default_interval))

    try:
        interval = int(interval_str)
        if interval < 60:
            logging.warning(
                f"Check interval {interval}s is very short (< 1 minute). "
                "This may cause rate limiting or excessive resource usage."
            )
        return interval
    except ValueError:
        logging.error(
            f"Invalid CHECK_INTERVAL_SECONDS value: '{interval_str}'. "
            f"Using default: {default_interval}s"
        )
        return default_interval


def format_interval(seconds: int) -> str:
    """Format interval in human-readable form."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"


def run_scheduler():
    """Main scheduler loop."""
    interval = get_check_interval()
    interval_str = format_interval(interval)

    # Setup basic logging for scheduler
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | SCHEDULER | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("=" * 70)
    logging.info("SaleNotificator2 - Scheduler Daemon Starting")
    logging.info("=" * 70)
    logging.info(f"Check interval: {interval_str} ({interval} seconds)")
    logging.info(f"Timezone: {os.environ.get('TZ', 'System default')}")
    logging.info("")

    run_count = 0

    try:
        while True:
            run_count += 1
            next_run = datetime.now() + timedelta(seconds=interval)

            logging.info(f"Starting check #{run_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info("-" * 70)

            # Run the main price checker
            try:
                exit_code = main()
                if exit_code != 0:
                    logging.error(f"Price check completed with errors (exit code: {exit_code})")
                else:
                    logging.info("Price check completed successfully")
            except Exception as e:
                logging.error(f"Unexpected error during price check: {e}", exc_info=True)

            logging.info("-" * 70)
            logging.info(f"Next check scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info(f"Sleeping for {interval_str}...")
            logging.info("")

            # Sleep until next check
            time.sleep(interval)

    except KeyboardInterrupt:
        logging.info("")
        logging.info("Scheduler stopped by user (Ctrl+C)")
        logging.info(f"Total checks performed: {run_count}")
        return 0
    except Exception as e:
        logging.error(f"Fatal error in scheduler: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(run_scheduler())
