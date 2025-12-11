#!/usr/bin/env python3
"""
SaleNotificator - Price Tracking and Notification System

This script checks product prices against configured thresholds
and sends email notifications when prices drop below the threshold.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from scraper import PriceScraper, ScraperError
from notifier import EmailNotifier, NotifierError


# Paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / 'config'
LOGS_DIR = BASE_DIR / 'logs'

# Config file
CONFIG_FILE = CONFIG_DIR / 'config.json'


def get_monthly_log_file() -> Path:
    """Generate log file path with year-month in the filename."""
    current_date = datetime.now()
    year_month = current_date.strftime('%Y-%m')
    log_filename = f'price_checks_{year_month}.log'
    return LOGS_DIR / log_filename


def setup_logging() -> logging.Logger:
    """Set up logging to both file and console."""
    LOGS_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger('SaleNotificator')
    logger.setLevel(logging.INFO)

    # File handler with monthly log rotation
    log_file = get_monthly_log_file()
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def load_json_config(path: Path) -> Dict:
    """Load a JSON configuration file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_config() -> Dict:
    """
    Load configuration from config.json.

    Returns a dict with keys: 'email', 'tracked_items', 'schedule' (if available)
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}\n"
            f"Please create config.json based on config.example.json"
        )

    config = load_json_config(CONFIG_FILE)

    # Ensure tracked_items is a list
    if 'tracked_items' not in config:
        config['tracked_items'] = []

    return config


def check_prices(logger: logging.Logger) -> List[Dict]:
    """Check all tracked items and return those below threshold."""
    # Load configuration
    config = load_config()
    items = config.get('tracked_items', [])

    scraper = PriceScraper()
    alerts = []

    logger.info(f"Starting price check for {len(items)} items")

    for item in items:
        if not item.get('enabled', True):
            logger.info(f"Skipping disabled item: {item['name']}")
            continue

        name = item['name']
        url = item['url']
        css_selector = item.get('css_selector', '.price')
        threshold = item['threshold']
        currency = item.get('currency', '')
        parameter = item.get('parameter', 'price')

        try:
            current_price = scraper.get_price(url, css_selector)

            if current_price < threshold:
                logger.info(
                    f"ALERT: {name} | {parameter}: {current_price:,.2f} {currency} "
                    f"(below threshold: {threshold:,.2f} {currency})"
                )
                alerts.append({
                    'name': name,
                    'url': url,
                    'current_price': current_price,
                    'threshold': threshold,
                    'currency': currency
                })
            else:
                logger.info(
                    f"OK: {name} | {parameter}: {current_price:,.2f} {currency} "
                    f"(threshold: {threshold:,.2f} {currency})"
                )

        except ScraperError as e:
            logger.error(f"ERROR: {name} | Failed to scrape: {e}")
        except Exception as e:
            logger.error(f"ERROR: {name} | Unexpected error: {e}")

    return alerts


def send_notifications(alerts: List[Dict], logger: logging.Logger) -> bool:
    """Send email notifications for price alerts."""
    if not alerts:
        logger.info("No price alerts to send")
        return True

    try:
        # Load configuration
        config = load_config()

        # Get email config
        email_config = config.get('email')
        if not email_config:
            logger.error("Email configuration not found in config.json")
            logger.info(f"Would have sent {len(alerts)} alert(s)")
            return False

        # Check if email is configured
        if email_config.get('sender_email') == 'your_email@gmail.com':
            logger.warning(
                "Email not configured. Please update your config file"
            )
            logger.info(f"Would have sent {len(alerts)} alert(s)")
            return False

        notifier = EmailNotifier(email_config)
        notifier.send_batch_alert(alerts)
        logger.info(f"Successfully sent email with {len(alerts)} alert(s)")
        return True

    except FileNotFoundError:
        logger.error("Email configuration file not found")
        return False
    except NotifierError as e:
        logger.error(f"Failed to send notification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending notification: {e}")
        return False


def main() -> int:
    """Main entry point."""
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("SaleNotificator - Price Check Started")
    logger.info("=" * 60)

    try:
        # Check prices
        alerts = check_prices(logger)

        # Send notifications if any alerts
        if alerts:
            send_notifications(alerts, logger)
        else:
            logger.info("All prices are at or above thresholds")

        logger.info("Price check completed successfully")
        return 0

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
