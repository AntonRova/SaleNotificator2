#!/usr/bin/env python3
"""
Scheduler daemon for continuous price checking.

This script runs the price checker based on a cron schedule defined in config.json.
The schedule can be modified in the config file without rebuilding the container.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from croniter import croniter

# Import main price checker
from main import main as run_price_check


# Paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / 'config'
CONFIG_FILE = CONFIG_DIR / 'config.json'

# Fallback to old config files if unified config doesn't exist
EMAIL_CONFIG_FILE = CONFIG_DIR / 'email_config.json'
TRACKED_ITEMS_FILE = CONFIG_DIR / 'tracked_items.json'


def load_config() -> Dict:
    """Load configuration from config.json or fallback to legacy files."""

    # Try unified config first
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Fallback to legacy config files
    logging.warning("Unified config.json not found. Using legacy config files.")
    logging.warning("Consider migrating to config.json for schedule configuration.")

    config = {
        "schedule": {
            "enabled": True,
            "cron": os.environ.get('CRON_SCHEDULE', '0 * * * *'),  # Default: hourly
            "run_on_startup": True,
            "description": "Fallback schedule from environment or default"
        }
    }

    # Load email config if it exists
    if EMAIL_CONFIG_FILE.exists():
        with open(EMAIL_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config["email"] = json.load(f)

    # Load tracked items if it exists
    if TRACKED_ITEMS_FILE.exists():
        with open(TRACKED_ITEMS_FILE, 'r', encoding='utf-8') as f:
            tracked_data = json.load(f)
            config["tracked_items"] = tracked_data.get("items", [])

    return config


def validate_cron_expression(cron_expr: str) -> bool:
    """Validate a cron expression."""
    try:
        croniter(cron_expr)
        return True
    except Exception as e:
        logging.error(f"Invalid cron expression '{cron_expr}': {e}")
        return False


def get_next_run_time(cron_expr: str, base_time: Optional[datetime] = None) -> datetime:
    """Calculate next run time based on cron expression."""
    if base_time is None:
        base_time = datetime.now()

    cron = croniter(cron_expr, base_time)
    return cron.get_next(datetime)


def format_time_until(target_time: datetime) -> str:
    """Format time until target in human-readable form."""
    now = datetime.now()
    delta = target_time - now

    total_seconds = int(delta.total_seconds())

    if total_seconds < 60:
        return f"{total_seconds} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        return f"{days}d {hours}h"


def run_scheduler():
    """Main scheduler loop using cron expressions from config."""

    # Setup basic logging for scheduler
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | SCHEDULER | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("=" * 70)
    logging.info("SaleNotificator2 - Config-Based Scheduler Starting")
    logging.info("=" * 70)

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return 1

    # Get schedule settings
    schedule_config = config.get("schedule", {})

    if not schedule_config.get("enabled", True):
        logging.warning("Scheduler is disabled in configuration!")
        logging.info("Set 'schedule.enabled' to true in config.json to enable.")
        return 0

    cron_expr = schedule_config.get("cron", "0 * * * *")
    run_on_startup = schedule_config.get("run_on_startup", True)
    timezone = schedule_config.get("timezone", os.environ.get('TZ', 'System default'))
    description = schedule_config.get("description", "Custom schedule")

    # Validate cron expression
    if not validate_cron_expression(cron_expr):
        logging.error("Invalid cron expression in config. Cannot start scheduler.")
        logging.info("Please fix the 'schedule.cron' field in config.json")
        logging.info("Example: '0 * * * *' for hourly checks")
        logging.info("Visit https://crontab.guru for help")
        return 1

    logging.info(f"Configuration loaded from: {CONFIG_FILE if CONFIG_FILE.exists() else 'legacy files'}")
    logging.info(f"Schedule: {description}")
    logging.info(f"Cron expression: {cron_expr}")
    logging.info(f"Timezone: {timezone}")
    logging.info(f"Run on startup: {run_on_startup}")
    logging.info("")

    run_count = 0

    # Calculate next run time
    next_run = get_next_run_time(cron_expr)
    logging.info(f"Next check scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Time until next check: {format_time_until(next_run)}")
    logging.info("")

    try:
        # Run immediately on startup if configured
        if run_on_startup:
            run_count += 1
            logging.info(f"=" * 70)
            logging.info(f"Starting STARTUP check #{run_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info("-" * 70)

            try:
                exit_code = run_price_check()
                if exit_code != 0:
                    logging.error(f"Price check completed with errors (exit code: {exit_code})")
                else:
                    logging.info("Price check completed successfully")
            except Exception as e:
                logging.error(f"Unexpected error during price check: {e}", exc_info=True)

            logging.info("-" * 70)
            logging.info("")

            # Recalculate next run after startup check
            next_run = get_next_run_time(cron_expr)
            logging.info(f"Next scheduled check: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info(f"Time until next check: {format_time_until(next_run)}")
            logging.info("")

        # Main scheduler loop
        while True:
            now = datetime.now()

            # Wait until next scheduled time
            if now >= next_run:
                run_count += 1
                logging.info(f"=" * 70)
                logging.info(f"Starting scheduled check #{run_count} at {now.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.info("-" * 70)

                # Run the main price checker
                try:
                    exit_code = run_price_check()
                    if exit_code != 0:
                        logging.error(f"Price check completed with errors (exit code: {exit_code})")
                    else:
                        logging.info("Price check completed successfully")
                except Exception as e:
                    logging.error(f"Unexpected error during price check: {e}", exc_info=True)

                logging.info("-" * 70)

                # Calculate next run time
                next_run = get_next_run_time(cron_expr)
                logging.info(f"Next scheduled check: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.info(f"Time until next check: {format_time_until(next_run)}")
                logging.info("")

            # Sleep for a short interval and check again
            # This allows for config reloading in the future if needed
            time.sleep(30)  # Check every 30 seconds

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
