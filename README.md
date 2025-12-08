# SaleNotificator2


A Docker-based price tracking and notification system that monitors product prices and sends email alerts when prices drop below configured thresholds.

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://github.com/AntonRova/SaleNotificator2)
[![TrueNAS](https://img.shields.io/badge/TrueNAS-compatible-green.svg)](TRUENAS_SIMPLE_DEPLOY.md)

---

## ⚠️ DISCLAIMER

**This application was developed with AI assistance (Claude by Anthropic).**

**USE AT YOUR OWN RISK**

- This software is provided "AS IS" without warranty of any kind
- The repository owner and contributors assume NO LIABILITY for any damages, losses, or issues arising from the use of this software
- You are responsible for:
  - Verifying the application works correctly for your use case
  - Ensuring compliance with terms of service of websites you monitor
  - Securing your configuration files and email credentials
  - Any consequences of automated price monitoring

**By using this software, you acknowledge that:**
- You use it entirely at your own risk
- The developers are not responsible for any harm, data loss, security issues, or other problems
- You are responsible for reviewing the code and understanding what it does before deployment
- Web scraping may violate some websites' terms of service - check before using

---

## Features

✨ **Price Monitoring**
- Track prices from multiple websites simultaneously
- Cloudflare bypass support for protected sites
- Configurable CSS selectors for flexible price extraction
- Multi-currency support

📧 **Smart Notifications**
- Email alerts when prices drop below thresholds
- Batch alerts (one email with multiple price drops)
- Detailed price information in alerts

📅 **Flexible Scheduling**
- Config-file-based cron scheduling
- No rebuild needed to change schedule
- Examples: hourly, twice daily, business hours only

🐳 **Docker Ready**
- Pre-built images via GitHub Actions
- TrueNAS SCALE custom app support
- Multi-architecture (amd64, arm64)

📊 **Logging**
- Monthly rotating log files
- Detailed price check history
- Easy troubleshooting

---

## Quick Start

### Option 1: TrueNAS SCALE Deployment (Recommended)

**5-minute deployment using pre-built Docker image:**

See **[TRUENAS_SIMPLE_DEPLOY.md](TRUENAS_SIMPLE_DEPLOY.md)** for step-by-step guide.

```bash
# 1. Create datasets in TrueNAS UI
# 2. Download config template
curl -o /mnt/pool/sale-notificator/config/config.json \
  https://raw.githubusercontent.com/AntonRova/SaleNotificator2/main/config/config.example.json

# 3. Edit config with your settings
nano /mnt/pool/sale-notificator/config/config.json

# 4. Deploy as Custom App using image:
#    ghcr.io/antonrova/salenotificator2:latest
```

### Option 2: Docker Compose

```bash
git clone https://github.com/AntonRova/SaleNotificator2.git
cd SaleNotificator2
cp config/config.example.json config/config.json
nano config/config.json  # Edit your settings
docker-compose up -d
```

### Option 3: Local Python

```bash
git clone https://github.com/AntonRova/SaleNotificator2.git
cd SaleNotificator2
pip install -r requirements.txt
cp config/config.example.json config/config.json
nano config/config.json  # Edit your settings
python src/scheduler.py  # Or python src/main.py for one-time check
```

---

## Configuration

### Unified Config (Recommended)

**File:** `config/config.json`

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",
    "recipient_email": "your_email@gmail.com",
    "use_tls": true
  },
  "schedule": {
    "enabled": true,
    "cron": "0 9,17 * * *",
    "timezone": "America/New_York",
    "run_on_startup": true,
    "description": "Twice daily at 9 AM and 5 PM"
  },
  "tracked_items": [
    {
      "name": "Product Name",
      "url": "https://example.com/product",
      "css_selector": ".price, .product-price",
      "threshold": 99.99,
      "currency": "USD",
      "enabled": true
    }
  ]
}
```

**Schedule Examples:**

| Schedule | Cron Expression |
|----------|----------------|
| Every hour | `0 * * * *` |
| Twice daily (9 AM & 5 PM) | `0 9,17 * * *` |
| Every 6 hours | `0 */6 * * *` |
| Business hours (Mon-Fri) | `0 9-17 * * 1-5` |

See **[CONFIG.md](CONFIG.md)** for complete configuration reference.

---

## Documentation

📚 **Deployment Guides:**
- **[TRUENAS_SIMPLE_DEPLOY.md](TRUENAS_SIMPLE_DEPLOY.md)** - 5-minute TrueNAS deployment (recommended)
- **[TRUENAS_DEPLOYMENT.md](TRUENAS_DEPLOYMENT.md)** - Detailed TrueNAS guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start for all platforms

📖 **Configuration & Usage:**
- **[CONFIG.md](CONFIG.md)** - Complete configuration reference
- **[SCHEDULING_OPTIONS.md](SCHEDULING_OPTIONS.md)** - Scheduling approaches explained

---

## Project Structure

```
SaleNotificator2/
├── .github/
│   └── workflows/
│       └── docker-build.yml       # GitHub Actions CI/CD
├── config/
│   ├── config.example.json        # Unified config template (recommended)
│   ├── email_config.example.json  # Legacy email config
│   └── tracked_items.example.json # Legacy tracked items
├── src/
│   ├── main.py                    # Price checker (one-time run)
│   ├── scheduler.py               # Scheduler daemon (continuous)
│   ├── scraper.py                 # Web scraping with Cloudflare bypass
│   ├── notifier.py                # Email notifications
│   └── config.py                  # Configuration loader
├── logs/                          # Monthly rotating logs
├── Dockerfile                     # Main Dockerfile
├── docker-compose.yml             # Docker Compose config
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## How It Works

1. **Scheduler** reads your `config.json` and cron schedule
2. **At scheduled times**, runs price checks for all enabled items
3. **Scraper** fetches product pages and extracts prices using CSS selectors
4. **Compares** current price against threshold
5. **Sends email** if price drops below threshold
6. **Logs** all activity to monthly files

---

## Requirements

- **Docker**: Recommended deployment method
- **Python 3.7+**: For local deployment
- **SMTP Email**: Gmail recommended (with App Password)

**Python Dependencies:**
- `requests` - HTTP library
- `cloudscraper` - Cloudflare bypass
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML processing
- `croniter` - Cron expression parsing

---

## GitHub Actions CI/CD

This repository includes automated Docker image building:

- ✅ Builds on every push to main/claude branches
- ✅ Publishes to GitHub Container Registry (GHCR)
- ✅ Multi-architecture support (amd64, arm64)
- ✅ Automatic versioning

**Pre-built images available at:**
```
ghcr.io/antonrova/salenotificator2:latest
```

---

## Usage Examples

### Check Prices Once

```bash
docker run --rm \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/antonrova/salenotificator2:latest \
  python3 src/main.py
```

### Run Continuously with Schedule

```bash
docker run -d \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/logs:/app/logs \
  -e TZ=America/New_York \
  ghcr.io/antonrova/salenotificator2:latest
```

---

## Security Best Practices

🔒 **Configuration Security:**
- Keep `config.json` secure with `chmod 600`
- Never commit config files to git
- Use app-specific passwords (not main email password)
- Mount config as read-only in Docker (`:ro`)

🔒 **Email Security:**
- For Gmail: Use [App Passwords](https://myaccount.google.com/apppasswords)
- Requires 2-factor authentication
- Never share your SMTP credentials

🔒 **General Security:**
- Review the code before deploying
- Keep the Docker image updated
- Monitor logs for suspicious activity
- Be aware of rate limiting on target websites

---

## Troubleshooting

### Price Not Found

**Problem:** CSS selector doesn't match the price element

**Solution:**
1. Visit product page in browser
2. Right-click price → "Inspect Element"
3. Find the CSS class/ID of price element
4. Update `css_selector` in config
5. Test with multiple selectors: `.price, .product-price, [data-price]`

### Email Not Sending

**Problem:** SMTP authentication fails

**Solution:**
1. For Gmail: Use App Password, not regular password
2. Enable 2-factor authentication on Gmail
3. Generate app password at https://myaccount.google.com/apppasswords
4. Check `sender_email` is not placeholder value
5. Verify port 587 is not blocked by firewall

### Container Keeps Restarting

**Problem:** Invalid configuration

**Solution:**
```bash
# Check logs
docker logs sale-notificator

# Validate JSON
cat config/config.json | python3 -m json.tool

# Check file permissions
ls -la config/config.json
```

### Schedule Not Working

**Problem:** Cron expression invalid or timezone mismatch

**Solution:**
1. Validate cron expression at https://crontab.guru
2. Check `timezone` matches your `TZ` environment variable
3. Use standard cron format (5 fields, not 6)
4. Review logs for schedule information

---

## Common Tasks

### Change Schedule

Edit `config/config.json`:
```json
{
  "schedule": {
    "cron": "0 */2 * * *"  // Change to every 2 hours
  }
}
```

Restart container:
```bash
docker restart sale-notificator
```

**No rebuild needed!**

### Add Products

Edit `config/config.json` and add to `tracked_items` array:
```json
{
  "tracked_items": [
    {
      "name": "New Product",
      "url": "https://example.com/new-product",
      "css_selector": ".price",
      "threshold": 149.99,
      "currency": "USD",
      "enabled": true
    }
  ]
}
```

Restart container to apply changes.

---

## Legal & Ethical Considerations

⚖️ **Before using this tool:**

1. **Check Terms of Service** - Some websites prohibit automated access
2. **Respect Rate Limits** - Don't overwhelm servers with requests
3. **Use Responsibly** - This is for personal use, not commercial scraping
4. **Privacy** - Don't scrape private or sensitive information
5. **Compliance** - Ensure your use complies with local laws

**The developers are not responsible for misuse of this software.**

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## License

This project is provided as-is without warranty. See disclaimer above.

---

## Support

📖 **Documentation:**
- [Configuration Guide](CONFIG.md)
- [TrueNAS Deployment](TRUENAS_SIMPLE_DEPLOY.md)
- [Scheduling Options](SCHEDULING_OPTIONS.md)

🐛 **Issues:**
- Report bugs via GitHub Issues
- Include logs and configuration (redact sensitive info)

---

## Acknowledgments

- Built with AI assistance (Claude by Anthropic)
- Uses `cloudscraper` for Cloudflare bypass
- Inspired by the need for automated price tracking

---

**Remember: Use at your own risk. The repository owner assumes no liability for any issues arising from the use of this software.**
