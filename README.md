# SaleNotificator2

A price tracking and notification system that monitors product prices and sends email alerts when prices drop below configured thresholds.

## Features

- Track prices from multiple websites
- Configurable CSS selectors for flexible price extraction
- Email notifications when prices drop below threshold
- Detailed logging of all price checks
- Support for different currencies

## Project Structure

```
SaleNotificator2/
├── config/
│   ├── tracked_items.json    # Products to track
│   └── email_config.json     # Email settings
├── logs/
│   └── price_checks.log      # Check results log
├── src/
│   ├── main.py               # Main entry point
│   ├── scraper.py            # Price scraping module
│   └── notifier.py           # Email notification module
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Tracked Items (`config/tracked_items.json`)

Add products to track:

```json
{
  "items": [
    {
      "name": "Product Name",
      "url": "https://example.com/product",
      "parameter": "price",
      "css_selector": ".price, .product-price",
      "threshold": 100.00,
      "currency": "USD",
      "enabled": true
    }
  ]
}
```

- `name`: Display name for the product
- `url`: Product page URL
- `parameter`: What you're tracking (e.g., "price", "cost")
- `css_selector`: CSS selector(s) to find the price element (comma-separated for multiple)
- `threshold`: Alert when price drops below this value
- `currency`: Currency code for display
- `enabled`: Set to false to skip this item

### Email Settings (`config/email_config.json`)

Configure email notifications:

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your_email@gmail.com",
  "sender_password": "your_app_password",
  "recipient_email": "recipient@example.com",
  "use_tls": true
}
```

**For Gmail:** Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## Usage

Run the price checker:

```bash
cd src
python main.py
```

### Automated Hourly Checks (Cron)

Add to crontab for hourly checks:

```bash
crontab -e
```

Add this line:
```
0 * * * * cd /path/to/SaleNotificator2/src && /usr/bin/python3 main.py
```

## Logs

All price checks are logged to `logs/price_checks.log`:

```
2024-01-15 10:00:00 | INFO | Starting price check for 2 items
2024-01-15 10:00:02 | INFO | OK: Product A | price: 150.00 USD (threshold: 100.00 USD)
2024-01-15 10:00:04 | INFO | ALERT: Product B | price: 89.99 USD (below threshold: 100.00 USD)
```

## Troubleshooting

### Price not being extracted

1. Open the product page in a browser
2. Right-click the price and select "Inspect"
3. Find the CSS class or ID of the price element
4. Update the `css_selector` in `tracked_items.json`

Common selectors to try:
- `.price`
- `.product-price`
- `.special-price`
- `[data-price]`
- `#product-price`
