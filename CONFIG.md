# Configuration Guide

SaleNotificator2 uses a single `config.json` file for all settings.

## Configuration (config.json)

The configuration file combines email settings, tracked items, and schedule configuration in a single file.

**Key Benefits:**
- ✅ Control the check schedule without rebuilding the Docker container
- ✅ All configuration in one place
- ✅ Easier to manage and backup
- ✅ Supports cron-based scheduling

### File Location

```
config/config.json
```

### Complete Example

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",
    "recipient_email": "recipient@example.com",
    "use_tls": true
  },
  "schedule": {
    "enabled": true,
    "cron": "0 * * * *",
    "timezone": "America/New_York",
    "run_on_startup": true,
    "description": "Every hour at minute 0"
  },
  "tracked_items": [
    {
      "name": "Example Product",
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

---

## Configuration Sections

### 1. Email Settings

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",
    "recipient_email": "recipient@example.com",
    "use_tls": true
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `smtp_server` | string | Yes | SMTP server hostname |
| `smtp_port` | number | Yes | SMTP server port (587 for TLS, 465 for SSL) |
| `sender_email` | string | Yes | Email address to send from |
| `sender_password` | string | Yes | Email password or app-specific password |
| `recipient_email` | string | Yes | Email address to receive alerts |
| `use_tls` | boolean | No | Use TLS encryption (default: true) |

#### Gmail Setup

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in `sender_password` (not your regular password)

#### Other Email Providers

- **Outlook/Hotmail**: `smtp.office365.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Use your provider's settings

---

### 2. Schedule Settings ⏰

This is the **key feature** of the unified config - control when price checks run!

```json
{
  "schedule": {
    "enabled": true,
    "cron": "0 * * * *",
    "timezone": "America/New_York",
    "run_on_startup": true,
    "description": "Every hour at minute 0"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | No | Enable/disable scheduled checks (default: true) |
| `cron` | string | Yes | Cron expression for schedule |
| `timezone` | string | No | Timezone for schedule (default: system TZ) |
| `run_on_startup` | boolean | No | Run check immediately when container starts (default: true) |
| `description` | string | No | Human-readable description of schedule |

#### Cron Expression Format

```
┌─── minute (0-59)
│ ┌─── hour (0-23)
│ │ ┌─── day of month (1-31)
│ │ │ ┌─── month (1-12)
│ │ │ │ ┌─── day of week (0-7, 0 and 7 are Sunday)
│ │ │ │ │
* * * * *
```

#### Common Schedule Examples

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every hour | `0 * * * *` | At minute 0 every hour |
| Every 30 minutes | `*/30 * * * *` or `0,30 * * * *` | Twice per hour |
| Every 2 hours | `0 */2 * * *` | At minute 0, every 2 hours |
| Every 6 hours | `0 */6 * * *` | 4 times per day |
| Daily at 9 AM | `0 9 * * *` | Once per day |
| Twice daily | `0 9,21 * * *` | At 9 AM and 9 PM |
| Weekdays at 9 AM | `0 9 * * 1-5` | Monday-Friday only |
| Every Monday at 10 AM | `0 10 * * 1` | Weekly |
| Business hours | `0 9-17 * * 1-5` | Every hour, 9 AM-5 PM, Mon-Fri |

#### Schedule Configuration Examples

**Check every 30 minutes:**
```json
{
  "schedule": {
    "enabled": true,
    "cron": "*/30 * * * *",
    "timezone": "America/New_York",
    "run_on_startup": true,
    "description": "Every 30 minutes"
  }
}
```

**Check twice daily (morning and evening):**
```json
{
  "schedule": {
    "enabled": true,
    "cron": "0 9,21 * * *",
    "timezone": "America/Los_Angeles",
    "run_on_startup": false,
    "description": "9 AM and 9 PM Pacific Time"
  }
}
```

**Check only on weekdays during business hours:**
```json
{
  "schedule": {
    "enabled": true,
    "cron": "0 9-17 * * 1-5",
    "timezone": "America/Chicago",
    "run_on_startup": true,
    "description": "Every hour, 9 AM-5 PM, Monday-Friday"
  }
}
```

**Temporarily disable scheduled checks:**
```json
{
  "schedule": {
    "enabled": false,
    "cron": "0 * * * *",
    "description": "Disabled for maintenance"
  }
}
```

#### Cron Help

- Use https://crontab.guru to build and test your cron expressions
- The scheduler validates your cron expression on startup
- Invalid expressions will prevent the container from starting (with error message)

---

### 3. Tracked Items

```json
{
  "tracked_items": [
    {
      "name": "Example Product",
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

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Product name (for alerts and logs) |
| `url` | string | Yes | Full product URL |
| `parameter` | string | No | What you're tracking (default: "price") |
| `css_selector` | string | Yes | CSS selector to find the price element |
| `threshold` | number | Yes | Alert when price falls below this value |
| `currency` | string | No | Currency code (USD, EUR, NZD, etc.) |
| `enabled` | boolean | No | Enable/disable this item (default: true) |

#### CSS Selector Examples

```json
// Single selector
"css_selector": ".price"

// Multiple selectors (tries each in order)
"css_selector": ".price, .product-price, [data-price]"

// Specific elements
"css_selector": "span.our-price"
"css_selector": "#product-price"
"css_selector": "div.price-box > span"
```

Use the included `find_amazon_selector.py` script to discover the correct selectors for websites.

---

## Changing the Schedule (Without Rebuilding!)

One of the key benefits of the unified config is that you can change the schedule without rebuilding the Docker container.

### Step-by-Step

1. **Edit your config file:**
   ```bash
   nano /mnt/your-pool/apps/sale-notificator/config/config.json
   ```

2. **Change the cron expression:**
   ```json
   {
     "schedule": {
       "cron": "0 */2 * * *"   // Changed from hourly to every 2 hours
     }
   }
   ```

3. **Restart the container:**
   ```bash
   # If using docker-compose
   docker-compose restart

   # If using TrueNAS Custom App
   # Go to Apps > Installed > sale-notificator > click "Restart"

   # If using docker directly
   docker restart sale-notificator
   ```

4. **Verify the new schedule:**
   ```bash
   docker logs sale-notificator | head -20
   ```

   You should see:
   ```
   Schedule: Every 2 hours
   Cron expression: 0 */2 * * *
   ```

**That's it!** No rebuild required.

---

## Configuration Best Practices

### Security

1. **Never commit config files to git** (they contain credentials)
2. **Use restrictive permissions:**
   ```bash
   chmod 600 /mnt/your-pool/apps/sale-notificator/config/config.json
   ```
3. **Mount config as read-only** in Docker (`:ro` flag)
4. **Use app-specific passwords** (not your main email password)

### Reliability

1. **Test cron expressions** at https://crontab.guru before deploying
2. **Start with conservative schedules** (hourly or longer) to avoid rate limiting
3. **Enable `run_on_startup`** to verify config on container restart
4. **Monitor logs** after changing configuration

### Maintenance

1. **Backup your config regularly:**
   ```bash
   cp config/config.json config/config.backup.$(date +%Y%m%d).json
   ```
2. **Document your CSS selectors** in case websites change
3. **Review and update selectors periodically** (websites change their HTML)
4. **Keep email credentials current** (rotate app passwords periodically)

---

## Troubleshooting

### Invalid Cron Expression

**Error:**
```
Invalid cron expression '0 * * * * *': Expected 5 fields, got 6
```

**Solution:** Standard cron uses 5 fields (minute, hour, day, month, weekday). Don't include seconds.

Correct: `0 * * * *`
Wrong: `0 * * * * *`

### Schedule Not Working

1. **Check container logs:**
   ```bash
   docker logs sale-notificator
   ```

2. **Verify cron expression is valid:**
   - Visit https://crontab.guru
   - Paste your cron expression
   - Verify it matches your intent

3. **Check timezone:**
   - Make sure `TZ` environment variable matches your `schedule.timezone`
   - Use standard timezone names (e.g., `America/New_York`, not `EST`)

### Config File Not Found

**Error:**
```
ERROR: Configuration files not found!
```

**Solutions:**
1. Verify file exists at `/mnt/your-pool/apps/sale-notificator/config/config.json`
2. Check volume mount in docker-compose.yml is correct
3. Verify file permissions allow Docker to read it
4. Check file name is exactly `config.json` (case-sensitive)

### Email Not Sending

1. **Check sender_email is not placeholder:**
   - Should NOT be: `your_email@gmail.com`
   - Should be: Your actual email

2. **For Gmail, use App Password:**
   - Not your regular Gmail password
   - Generate at: https://myaccount.google.com/apppasswords

3. **Check SMTP settings for your provider**

---

## Example Configurations

### Minimal Config (Hourly Checks)

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "alerts@example.com",
    "sender_password": "app-password-here",
    "recipient_email": "you@example.com",
    "use_tls": true
  },
  "schedule": {
    "enabled": true,
    "cron": "0 * * * *"
  },
  "tracked_items": [
    {
      "name": "Gaming Laptop",
      "url": "https://store.example.com/laptop-xyz",
      "css_selector": ".price-current",
      "threshold": 999.99,
      "currency": "USD",
      "enabled": true
    }
  ]
}
```

### Advanced Config (Multiple Items, Custom Schedule)

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "price.alerts@gmail.com",
    "sender_password": "xyzw abcd efgh ijkl",
    "recipient_email": "myemail@example.com",
    "use_tls": true
  },
  "schedule": {
    "enabled": true,
    "cron": "0 */2 * * *",
    "timezone": "America/New_York",
    "run_on_startup": true,
    "description": "Check every 2 hours"
  },
  "tracked_items": [
    {
      "name": "RTX 4090 Graphics Card",
      "url": "https://www.newegg.com/product-xyz",
      "parameter": "price",
      "css_selector": ".price-current",
      "threshold": 1599.99,
      "currency": "USD",
      "enabled": true
    },
    {
      "name": "PlayStation 5",
      "url": "https://www.amazon.com/dp/B0XXXXXXX",
      "parameter": "price",
      "css_selector": "#priceblock_ourprice, .a-price-whole",
      "threshold": 499.99,
      "currency": "USD",
      "enabled": true
    },
    {
      "name": "Nintendo Switch OLED",
      "url": "https://www.bestbuy.com/product-abc",
      "parameter": "price",
      "css_selector": ".priceView-customer-price span",
      "threshold": 329.99,
      "currency": "USD",
      "enabled": false
    }
  ]
}
```

---

## Schedule Change Examples

### From Hourly to Every 6 Hours

**Before:**
```json
"cron": "0 * * * *"
```

**After:**
```json
"cron": "0 */6 * * *"
```

**Apply:**
```bash
docker-compose restart
```

### From Hourly to Twice Daily

**Before:**
```json
"cron": "0 * * * *"
```

**After:**
```json
{
  "cron": "0 9,21 * * *",
  "description": "Check at 9 AM and 9 PM"
}
```

**Apply:**
```bash
docker restart sale-notificator
```

### Temporarily Disable Checks

**Before:**
```json
{
  "enabled": true,
  "cron": "0 * * * *"
}
```

**After:**
```json
{
  "enabled": false,
  "cron": "0 * * * *"
}
```

**Apply:**
```bash
docker-compose restart
# Container will start but not run checks
```

---

## Additional Resources

- **Cron Expression Tester**: https://crontab.guru
- **Timezone Database**: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
- **CSS Selector Guide**: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors
- **Gmail App Passwords**: https://support.google.com/accounts/answer/185833

---

For deployment instructions, see `TRUENAS_DEPLOYMENT.md`.

For scheduling implementation details, see `SCHEDULING_OPTIONS.md`.
