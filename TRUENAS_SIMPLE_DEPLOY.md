# TrueNAS Simple Deployment Guide

**No building, no scripts, just deploy!** 🚀

This guide uses the **pre-built Docker image** from GitHub Container Registry.

---

## Overview

**Time to deploy:** ~5 minutes
**Technical level:** Beginner
**What you need:**
- TrueNAS SCALE 24.10+
- Gmail account (or other SMTP email)

---

## Step 1: Create Datasets (TrueNAS Web UI)

### 1.1 Create Parent Dataset

1. Go to **Storage** → **Datasets**
2. Click **Add Dataset**
   - **Name**: `sale-notificator`
   - **Dataset Preset**: `Generic`
   - Click **Save**

### 1.2 Create Config Subdataset

1. Click on the `sale-notificator` dataset you just created
2. Click **Add Dataset**
   - **Name**: `config`
   - **Dataset Preset**: `Generic`
   - Click **Save**

### 1.3 Create Logs Subdataset

1. With `sale-notificator` still selected, click **Add Dataset** again
   - **Name**: `logs`
   - **Dataset Preset**: `Generic`
   - Click **Save**

**Result:** You now have a nested structure:
- `/mnt/your-pool/sale-notificator/` (parent)
- `/mnt/your-pool/sale-notificator/config/` (child)
- `/mnt/your-pool/sale-notificator/logs/` (child)

---

## Step 2: Create Configuration File

### 2.1 Download Example Config

**Option A: Using TrueNAS Shell**

Click the Shell icon (top right), then run:

```bash
# Download example config
curl -o /mnt/your-pool/sale-notificator/config/config.json \
  https://raw.githubusercontent.com/AntonRova/SaleNotificator2/claude/docker-truenas-setup-0144QCmGtmmnf5Syv1GLrYbi/config/config.example.json
```

**Option B: Manual Creation**

In TrueNAS Shell:
```bash
nano /mnt/your-pool/sale-notificator/config/config.json
```

Paste this content:
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
      "name": "Example Product",
      "url": "https://www.amazon.com/dp/PRODUCT_ID",
      "parameter": "price",
      "css_selector": "#priceblock_ourprice, .a-price-whole",
      "threshold": 99.99,
      "currency": "USD",
      "enabled": true
    }
  ]
}
```

Save with `Ctrl+O`, `Enter`, then `Ctrl+X`

### 2.2 Edit the Config

Still in TrueNAS Shell:
```bash
nano /mnt/your-pool/sale-notificator/config/config.json
```

**Update these values:**

1. **Email settings:**
   - `sender_email`: Your Gmail address
   - `sender_password`: Your Gmail App Password ([Get it here](https://myaccount.google.com/apppasswords))
   - `recipient_email`: Where to receive alerts

2. **Schedule:** (already set to 9 AM and 5 PM)
   - Change `cron` if you want a different schedule
   - Change `timezone` to your timezone

3. **Products to track:**
   - Update `name`, `url`, `css_selector`, `threshold`
   - Add more items by copying the example

**Save and exit**

### 2.3 Secure the File

```bash
chmod 600 /mnt/your-pool/sale-notificator/config/config.json
```

---

## Step 3: Deploy as TrueNAS Custom App

### 3.1 Open Custom App

1. Go to **Apps** in the TrueNAS web interface
2. Click **Discover Apps**
3. Click **Custom App** (top right button)

### 3.2 Configure the Application

Fill in the form:

#### **Application Name**
```
Application Name: sale-notificator
Version: 1.0.0
```

#### **Image Configuration**

**IMPORTANT:** Use the pre-built image from GitHub!

```
Image Repository: ghcr.io/antonrova/salenotificator2
Image Tag: latest
Image Pull Policy: Always
```

#### **Container Environment Variables**

Click **Add** to add one variable:

```
Name: TZ
Value: America/New_York
```
(Change to your timezone)

#### **Storage - Host Path Volumes**

Click **Add** under "Host Path Volumes" **TWICE**:

**Volume 1: Config (Read-Only)**
```
Type: Host Path
Host Path: /mnt/your-pool/sale-notificator/config
Mount Path: /app/config
☑ Read Only: CHECKED
```

**Volume 2: Logs (Writable)**
```
Type: Host Path
Host Path: /mnt/your-pool/sale-notificator/logs
Mount Path: /app/logs
☐ Read Only: UNCHECKED
```

#### **Resources (Optional but Recommended)**

```
☑ Enable Resource Limits
CPU Limit: 1
Memory Limit: 256 MiB
```

**Note:** CPU limit must be a whole number (1, 2, etc.).

#### **Advanced DNS Settings**

Leave as default

#### **Restart Policy**

```
Restart Policy: Unless Stopped
```

### 3.3 Deploy!

1. Review all settings
2. Click **Install**
3. Wait 30-60 seconds

---

## Step 4: Verify It's Working

### 4.1 Check Container Status

1. Go to **Apps** → **Installed**
2. Find `sale-notificator`
3. Status should be **Active** (green)

### 4.2 View Logs

**Method 1: TrueNAS Web UI**
1. Click on `sale-notificator`
2. Click **Logs** button

**Method 2: Shell**
```bash
docker logs sale-notificator
```

**What you should see:**
```
SaleNotificator2 Docker Container Starting...
✓ Found unified config.json
  Schedule will be read from config.json

SaleNotificator2 - Config-Based Scheduler Starting
======================================================================
Schedule: Twice daily at 9 AM and 5 PM
Cron expression: 0 9,17 * * *
Timezone: America/New_York
Run on startup: True

Starting STARTUP check #1 at 2024-12-08 15:30:00
----------------------------------------------------------------------
Starting price check for 1 items
OK: Example Product | price: 129.99 USD (threshold: 99.99 USD)
All prices are at or above thresholds
Price check completed successfully
----------------------------------------------------------------------
Next scheduled check: 2024-12-08 17:00:00
Time until next check: 1h 30m
```

### 4.3 Check Log Files

In TrueNAS Shell:
```bash
ls -lh /mnt/your-pool/sale-notificator/logs/
```

You should see:
```
price_checks_2024-12.log
```

View it:
```bash
tail -f /mnt/your-pool/sale-notificator/logs/*.log
```

---

## That's It! 🎉

Your price tracker is now running and will check prices at **9 AM and 5 PM** every day.

---

## Common Tasks

### Change the Schedule

1. Edit config:
   ```bash
   nano /mnt/your-pool/sale-notificator/config/config.json
   ```

2. Change the `cron` value:
   ```json
   {
     "schedule": {
       "cron": "0 */6 * * *"  // Every 6 hours
     }
   }
   ```

3. Restart the app:
   - Go to **Apps** → **Installed** → `sale-notificator`
   - Click **Stop**, then **Start**

**No rebuild needed!**

### Add More Products

1. Edit config:
   ```bash
   nano /mnt/your-pool/sale-notificator/config/config.json
   ```

2. Add to the `tracked_items` array:
   ```json
   {
     "tracked_items": [
       {
         "name": "Product 1",
         "url": "https://example.com/product1",
         "css_selector": ".price",
         "threshold": 99.99,
         "currency": "USD",
         "enabled": true
       },
       {
         "name": "Product 2",
         "url": "https://example.com/product2",
         "css_selector": ".our-price",
         "threshold": 149.99,
         "currency": "USD",
         "enabled": true
       }
     ]
   }
   ```

3. Restart the app

### Update to Latest Version

When there's a new version:

1. Go to **Apps** → **Installed** → `sale-notificator`
2. Click **Edit**
3. Scroll to **Image Configuration**
4. Change **Image Pull Policy** to `Always` (if not already)
5. Click **Update**

TrueNAS will pull the latest image from GitHub automatically!

---

## Schedule Examples

Change the `cron` field in your config:

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every hour | `0 * * * *` | Top of every hour |
| Every 2 hours | `0 */2 * * *` | 12 times per day |
| Every 6 hours | `0 */6 * * *` | 4 times per day |
| **Twice daily** | `0 9,17 * * *` | **9 AM and 5 PM** ⭐ |
| Daily at 9 AM | `0 9 * * *` | Once per day |
| Business hours | `0 9-17 * * 1-5` | Hourly, 9-5, Mon-Fri |

Use https://crontab.guru to create custom schedules!

---

## Troubleshooting

### Container Won't Start

**Check logs for error messages:**
```bash
docker logs sale-notificator
```

**Common issues:**
1. **Invalid JSON in config:**
   ```bash
   cat /mnt/your-pool/sale-notificator/config/config.json | python3 -m json.tool
   ```
   If you see an error, fix the JSON syntax

2. **Config file not found:**
   ```bash
   ls -la /mnt/your-pool/sale-notificator/config/config.json
   ```
   Make sure it exists

3. **Wrong volume paths:**
   - Double-check paths in Custom App configuration
   - Must match your actual dataset paths

### Email Not Sending

1. **For Gmail:**
   - Use App Password, not regular password
   - Get it at: https://myaccount.google.com/apppasswords
   - Requires 2-factor authentication enabled

2. **Check sender_email:**
   - Must NOT be `your_email@gmail.com`
   - Must be your actual email

3. **Test SMTP connection:**
   ```bash
   docker exec sale-notificator python3 -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587)"
   ```

### Prices Not Found

**CSS selector may be wrong:**
1. Visit the product page in a browser
2. Right-click the price → **Inspect Element**
3. Find the class or ID of the price element
4. Update `css_selector` in config
5. Restart the app

---

## Directory Structure Reference

```
/mnt/your-pool/
└── sale-notificator/            # Parent dataset
    ├── config/                  # Config subdataset
    │   └── config.json          # Your configuration
    └── logs/                    # Logs subdataset
        └── price_checks_2024-12.log  # Monthly logs
```

---

## Benefits of This Approach

✅ **No building on TrueNAS** - Uses pre-built image from GitHub
✅ **Auto-updates** - Just pull latest image
✅ **Smaller footprint** - No build tools on TrueNAS
✅ **Faster deployment** - Download vs build
✅ **Consistent** - Same image everywhere
✅ **Professional** - CI/CD pipeline with GitHub Actions

---

## Support

- **Configuration Guide:** [CONFIG.md](CONFIG.md)
- **Cron Help:** https://crontab.guru
- **Gmail App Passwords:** https://support.google.com/accounts/answer/185833

---

**Enjoy automated price tracking!** 📊📉🔔
