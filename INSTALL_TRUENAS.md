# SaleNotificator2 - Complete TrueNAS Installation Guide

**Time to complete:** 10 minutes
**Difficulty:** Beginner-friendly
**TrueNAS version:** SCALE 24.10+

This guide will walk you through every single step to get SaleNotificator2 running on your TrueNAS server.

---

## 📋 What You'll Need

Before starting, make sure you have:

- [ ] TrueNAS SCALE 24.10 or later
- [ ] Admin access to TrueNAS web interface
- [ ] Gmail account (or other email provider)
- [ ] Gmail App Password ([Get it here](https://myaccount.google.com/apppasswords))
- [ ] 5-10 minutes of your time

---

## 🎯 Part 1: Prepare Your TrueNAS Storage (5 minutes)

### Step 1.1: Open TrueNAS Web Interface

1. Open your web browser
2. Navigate to your TrueNAS IP address:
   ```
   http://your-truenas-ip
   ```
   Example: `http://192.168.1.100`

3. Log in with your admin credentials

### Step 1.2: Navigate to Datasets

1. Click **"Storage"** in the left sidebar
2. Click **"Datasets"** (or it may already be showing)
3. You'll see your pools listed

### Step 1.3: Create Parent Dataset

1. **Select your pool** (click on it)
   - Example: `tank`, `main-pool`, or whatever your pool is named

2. Click the **"Add Dataset"** button (usually top right)

3. **Fill in the form:**
   - **Name**: `sale-notificator`
   - **Dataset Preset**: `Generic`
   - **Compression**: Leave default
   - **Share Type**: Leave as `Generic`

4. Click **"Save"**

5. **Wait** for the dataset to be created (should be instant)

### Step 1.4: Create Config Subdataset

1. **Click on** the `sale-notificator` dataset you just created
   - It should be highlighted/selected now

2. Click **"Add Dataset"** again

3. **Fill in the form:**
   - **Name**: `config`
   - **Dataset Preset**: `Generic`

4. Click **"Save"**

### Step 1.5: Create Logs Subdataset

1. Make sure `sale-notificator` is still selected

2. Click **"Add Dataset"** one more time

3. **Fill in the form:**
   - **Name**: `logs`
   - **Dataset Preset**: `Generic`

4. Click **"Save"**

### ✅ Verify Your Datasets

You should now see this structure:
```
your-pool
└── sale-notificator
    ├── config
    └── logs
```

**Note your full path** - it will be something like:
- `/mnt/tank/sale-notificator/config`
- `/mnt/tank/sale-notificator/logs`

**Write these down!** You'll need them later.

---

## 📝 Part 2: Create Configuration File (3 minutes)

### Step 2.1: Open TrueNAS Shell

1. Look at the **top right** of the TrueNAS interface
2. Click the **Shell icon** (looks like `>_` or a terminal)
3. A black command-line window will open

### Step 2.2: Download Example Config

**Copy and paste this command** into the shell (replace `tank` with your pool name):

```bash
curl -o /mnt/tank/sale-notificator/config/config.json \
  https://raw.githubusercontent.com/AntonRova/SaleNotificator2/main/config/config.example.json
```

**Press Enter**

You should see:
```
  % Total    % Received...
100  1234  100  1234    0     0   5678      0 --:--:-- --:--:-- --:--:--  5678
```

✅ Config file downloaded!

### Step 2.3: Edit the Config File

**Type this command** (replace `tank` with your pool):

```bash
nano /mnt/tank/sale-notificator/config/config.json
```

**Press Enter**

The file will open in a text editor.

### Step 2.4: Update Email Settings

Use arrow keys to navigate. Update these values:

**Find this section:**
```json
"email": {
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your_email@gmail.com",     ← CHANGE THIS
  "sender_password": "your_app_password",      ← CHANGE THIS
  "recipient_email": "your_email@gmail.com",   ← CHANGE THIS
  "use_tls": true
},
```

**Change to:**
```json
"email": {
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "myemail@gmail.com",        ← Your Gmail
  "sender_password": "abcd efgh ijkl mnop",   ← Your App Password
  "recipient_email": "myemail@gmail.com",     ← Where to receive alerts
  "use_tls": true
},
```

**Important:** For Gmail App Password:
1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Create an App Password for "Mail"
4. Copy the 16-character password (it will have spaces)
5. Paste it as the `sender_password`

### Step 2.5: Update Schedule (Optional)

The default is **twice daily at 9 AM and 5 PM**.

If that's good, **skip this step**.

To change it, find:
```json
"schedule": {
  "enabled": true,
  "cron": "0 9,17 * * *",              ← Change this if needed
  "timezone": "America/New_York",      ← Change to your timezone
  "run_on_startup": true,
  "description": "Twice daily at 9 AM and 5 PM"
},
```

**Common schedules:**
- Every hour: `"cron": "0 * * * *"`
- Every 6 hours: `"cron": "0 */6 * * *"`
- Daily at 9 AM: `"cron": "0 9 * * *"`

**Common timezones:**
- `America/New_York` - Eastern
- `America/Chicago` - Central
- `America/Los_Angeles` - Pacific
- `Europe/London` - UK

### Step 2.6: Update Products to Track

Find the `tracked_items` section:

```json
"tracked_items": [
  {
    "name": "Example Product",                           ← Product name
    "url": "https://www.amazon.com/dp/PRODUCT_ID",      ← Product URL
    "parameter": "price",
    "css_selector": "#priceblock_ourprice, .a-price-whole",  ← Price selector
    "threshold": 99.99,                                  ← Alert when below this
    "currency": "USD",
    "enabled": true
  }
]
```

**Update:**
- `name`: A name you'll recognize
- `url`: The full product URL
- `threshold`: The price to alert you when it drops below
- `currency`: USD, EUR, GBP, NZD, etc.

**To add more products**, copy the entire `{ ... }` block and add a comma:

```json
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
    "css_selector": ".price",
    "threshold": 149.99,
    "currency": "USD",
    "enabled": true
  }
]
```

### Step 2.7: Save the File

1. Press `Ctrl + O` (that's the letter O, not zero)
2. Press `Enter` to confirm
3. Press `Ctrl + X` to exit

### Step 2.8: Secure the File

**Type this command:**

```bash
chmod 600 /mnt/tank/sale-notificator/config/config.json
```

**Press Enter**

✅ Config file is now secured!

### Step 2.9: Verify the File

**Type this command to check it's valid JSON:**

```bash
cat /mnt/tank/sale-notificator/config/config.json | python3 -m json.tool
```

**Press Enter**

If you see nicely formatted JSON, ✅ it's valid!

If you see an error, you have a typo. Go back and fix it:
```bash
nano /mnt/tank/sale-notificator/config/config.json
```

**Close the shell** by clicking the X or typing `exit`.

---

## 🐳 Part 3: Deploy as Custom App (5 minutes)

### Step 3.1: Navigate to Apps

1. Click **"Apps"** in the left sidebar of TrueNAS
2. You'll see the Apps dashboard

### Step 3.2: Open Custom App Dialog

1. Click **"Discover Apps"** (top of the page)
2. Click the **"Custom App"** button
   - Usually top right corner
   - Looks like a button with "Custom App" text

A form will appear with many fields.

### Step 3.3: Fill in Application Name

**Scroll to the top of the form.**

**Application Name Section:**
```
Application Name: sale-notificator
Version: 1.0.0
```

### Step 3.4: Configure Container Image

**Find "Image Configuration" section.**

**CRITICAL - Use the pre-built image from GitHub:**

```
Image Repository: ghcr.io/antonrova/salenotificator2
Image Tag: latest
Image Pull Policy: Always
```

**Important:**
- Type this **exactly** as shown
- Include the full path: `ghcr.io/antonrova/salenotificator2`
- Tag is just: `latest`

### Step 3.5: Set Environment Variables

**Scroll down to "Container Environment Variables"**

Click the **"Add"** button

**Fill in:**
```
Environment Variable Name: TZ
Environment Variable Value: America/New_York
```

(Change `America/New_York` to your timezone if different)

### Step 3.6: Configure Storage Volumes

**This is the most important part!**

**Scroll down to "Storage and Persistence"**

Under **"Host Path Volumes"**, click **"Add"** button **TWICE** (you need two volumes)

#### Volume 1: Config (Read-Only)

**Click "Add" for the first volume:**

```
Type: Host Path

Host Path: /mnt/tank/sale-notificator/config
           ↑
           Replace 'tank' with your pool name!

Mount Path: /app/config

☑ Read Only: CHECK THIS BOX ✅
```

**Double-check:**
- Host Path matches YOUR pool name
- Mount Path is exactly `/app/config`
- **Read Only is CHECKED**

#### Volume 2: Logs (Writable)

**Click "Add" for the second volume:**

```
Type: Host Path

Host Path: /mnt/tank/sale-notificator/logs
           ↑
           Replace 'tank' with your pool name!

Mount Path: /app/logs

☐ Read Only: LEAVE UNCHECKED ❌
```

**Double-check:**
- Host Path matches YOUR pool name
- Mount Path is exactly `/app/logs`
- **Read Only is UNCHECKED**

### Step 3.7: Set Resource Limits (Optional but Recommended)

**Scroll to "Resources Configuration"**

```
☑ Enable Resource Limits

CPU Limit: 0.5
Memory Limit: 256 (MiB)
```

This prevents the app from using too much resources.

### Step 3.8: Set Restart Policy

**Scroll to "Advanced Settings" or "Restart Policy"**

```
Restart Policy: Unless Stopped
```

### Step 3.9: Review and Install

1. **Scroll back to the top** and review all settings
2. Make sure:
   - Image is: `ghcr.io/antonrova/salenotificator2:latest`
   - Both volumes are configured correctly
   - Host paths match YOUR pool name

3. Click the **"Install"** button (usually at the bottom)

### Step 3.10: Wait for Deployment

You'll see a progress indicator.

**Wait 30-60 seconds** while TrueNAS:
- Pulls the Docker image
- Creates the container
- Starts the application

---

## ✅ Part 4: Verify It's Working (2 minutes)

### Step 4.1: Check App Status

1. Go to **Apps** → **Installed**
2. Find **sale-notificator** in the list
3. Status should show: **Active** with a **green icon** ✅

If you see red or yellow, proceed to troubleshooting below.

### Step 4.2: View Logs

**Method 1: TrueNAS Web Interface**

1. Click on the **sale-notificator** app card
2. Click the **"Logs"** button (looks like a document icon)
3. Logs will appear in a window

**Method 2: Shell Command**

1. Open TrueNAS Shell (click `>_` icon)
2. Type:
   ```bash
   docker logs sale-notificator
   ```
3. Press Enter

### Step 4.3: What You Should See in Logs

**Good logs look like this:**

```
SaleNotificator2 Docker Container Starting...
Configuration directory: /app/config
Logs directory: /app/logs

✓ Found unified config.json
  Schedule will be read from config.json

Starting scheduler daemon...

======================================================================
SaleNotificator2 - Config-Based Scheduler Starting
======================================================================
Configuration loaded from: /app/config/config.json
Schedule: Twice daily at 9 AM and 5 PM
Cron expression: 0 9,17 * * *
Timezone: America/New_York
Run on startup: True

======================================================================
Starting STARTUP check #1 at 2024-12-08 15:30:00
----------------------------------------------------------------------
SaleNotificator - Price Check Started
======================================================================
Starting price check for 1 items
OK: Example Product | price: 129.99 USD (threshold: 99.99 USD)
All prices are at or above thresholds
Price check completed successfully
----------------------------------------------------------------------

Next scheduled check: 2024-12-08 17:00:00
Time until next check: 1h 30m
```

**Key things to look for:**
- ✅ "Found unified config.json"
- ✅ Your schedule shows up correctly
- ✅ "Starting STARTUP check"
- ✅ Your products are being checked
- ✅ "Next scheduled check" shows the right time

### Step 4.4: Check Log Files on Disk

1. Open TrueNAS Shell
2. Type:
   ```bash
   ls -lh /mnt/tank/sale-notificator/logs/
   ```
3. Press Enter

**You should see:**
```
price_checks_2024-12.log
```

**View the log:**
```bash
tail -20 /mnt/tank/sale-notificator/logs/price_checks_2024-12.log
```

---

## 🎉 You're Done!

Your price tracker is now:
- ✅ Running on TrueNAS
- ✅ Checking prices at 9 AM and 5 PM (or your custom schedule)
- ✅ Will send you email alerts when prices drop
- ✅ Logging all activity to monthly files
- ✅ Restarting automatically if it crashes

---

## 🔧 Troubleshooting

### Problem: Container Status is Red/Stopped

**Check the logs:**
```bash
docker logs sale-notificator
```

**Common causes:**

1. **"Config file not found"**
   - Check your host paths in the Custom App settings
   - Make sure `/mnt/tank/sale-notificator/config/config.json` exists
   - Verify you used the correct pool name

2. **"Invalid JSON"**
   - Your config file has a syntax error
   - Validate it:
     ```bash
     cat /mnt/tank/sale-notificator/config/config.json | python3 -m json.tool
     ```
   - Fix any errors shown

3. **"Permission denied"**
   - Run:
     ```bash
     chmod 600 /mnt/tank/sale-notificator/config/config.json
     chmod 755 /mnt/tank/sale-notificator/config
     chmod 755 /mnt/tank/sale-notificator/logs
     ```

### Problem: Email Not Sending

**Check logs for SMTP errors:**
```bash
docker logs sale-notificator | grep -i email
```

**Common causes:**

1. **Using regular Gmail password instead of App Password**
   - You MUST use an App Password
   - Get it at: https://myaccount.google.com/apppasswords

2. **Email still set to placeholder**
   - Check config:
     ```bash
     cat /mnt/tank/sale-notificator/config/config.json | grep sender_email
     ```
   - Must NOT be: `your_email@gmail.com`

3. **2-Factor Authentication not enabled**
   - Gmail requires 2FA for App Passwords
   - Enable it in your Google account settings

### Problem: Prices Not Being Found

**Check the CSS selector:**

1. Open the product page in your browser
2. Right-click on the price
3. Select "Inspect" or "Inspect Element"
4. Look at the HTML for the price element
5. Update the `css_selector` in your config

**Common selectors:**
- `.price`
- `.product-price`
- `#priceblock_ourprice`
- `.a-price-whole`
- `[data-price]`

Try multiple selectors separated by commas:
```json
"css_selector": ".price, .product-price, [data-price]"
```

### Problem: Container Keeps Restarting

**View restart logs:**
```bash
docker logs --tail 100 sale-notificator
```

**Common causes:**

1. **Invalid cron expression**
   - Test it at: https://crontab.guru
   - Must be 5 fields: `minute hour day month weekday`
   - Example: `0 9,17 * * *` (not `0 9,17 * * * *` with 6 fields)

2. **Timezone doesn't exist**
   - Use standard timezone names
   - List: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
   - Example: `America/New_York` not `EST`

### Problem: Can't Pull Docker Image

**Error:** "Failed to pull image"

**Solutions:**

1. **Check internet connection** on TrueNAS:
   ```bash
   ping -c 3 google.com
   ```

2. **Try pulling manually:**
   ```bash
   docker pull ghcr.io/antonrova/salenotificator2:latest
   ```

3. **Check image exists:**
   - Go to: https://github.com/AntonRova/SaleNotificator2/pkgs/container/salenotificator2
   - Verify the image is public

---

## 📊 Managing Your App

### Restart the App

**Method 1: TrueNAS Web Interface**
1. Go to **Apps** → **Installed**
2. Click on **sale-notificator**
3. Click **"Stop"**
4. Wait for it to stop
5. Click **"Start"**

**Method 2: Shell**
```bash
docker restart sale-notificator
```

### Stop the App

```bash
docker stop sale-notificator
```

### Start the App

```bash
docker start sale-notificator
```

### View Real-Time Logs

```bash
docker logs -f sale-notificator
```

Press `Ctrl+C` to stop viewing.

### Update to Latest Version

When a new version is released:

1. Go to **Apps** → **Installed**
2. Click on **sale-notificator**
3. Click **"Edit"**
4. Click **"Update"** (pulls latest image)
5. App will restart automatically

Or via shell:
```bash
docker pull ghcr.io/antonrova/salenotificator2:latest
docker restart sale-notificator
```

---

## 🔄 Common Tasks

### Change the Schedule

1. Edit config:
   ```bash
   nano /mnt/tank/sale-notificator/config/config.json
   ```

2. Change the `cron` value:
   ```json
   "cron": "0 */6 * * *"  // Every 6 hours
   ```

3. Save (`Ctrl+O`, `Enter`, `Ctrl+X`)

4. Restart:
   ```bash
   docker restart sale-notificator
   ```

**No rebuild needed!**

### Add More Products

1. Edit config:
   ```bash
   nano /mnt/tank/sale-notificator/config/config.json
   ```

2. Add to `tracked_items` array (don't forget the comma!):
   ```json
   "tracked_items": [
     {
       "name": "Product 1",
       ...
     },
     {
       "name": "Product 2",
       ...
     }
   ]
   ```

3. Save and restart

### Disable a Product Temporarily

In config, set `"enabled": false`:

```json
{
  "name": "Product Name",
  "url": "...",
  "threshold": 99.99,
  "enabled": false  ← Change to false
}
```

### Test Email Manually

Set a very high threshold to trigger an alert:

```json
"threshold": 99999.99
```

Restart the app. You should get an email immediately!

Don't forget to change it back after testing.

---

## 📁 Your File Structure

After setup, you'll have:

```
/mnt/tank/sale-notificator/
├── config/
│   └── config.json                    # Your configuration
└── logs/
    └── price_checks_2024-12.log       # Monthly logs
```

**Logs rotate monthly** - one file per month:
- `price_checks_2024-12.log`
- `price_checks_2025-01.log`
- etc.

---

## 🔐 Security Notes

1. **Protect your config:**
   ```bash
   chmod 600 /mnt/tank/sale-notificator/config/config.json
   ```

2. **Never share your config file** - it contains passwords!

3. **Backup your config:**
   ```bash
   cp /mnt/tank/sale-notificator/config/config.json \
      /mnt/tank/sale-notificator/config/config.backup.json
   ```

4. **Use App Passwords, not your real Gmail password**

5. **Keep TrueNAS updated**

---

## 🎯 Quick Reference

### View Logs
```bash
docker logs sale-notificator
tail -f /mnt/tank/sale-notificator/logs/*.log
```

### Restart App
```bash
docker restart sale-notificator
```

### Edit Config
```bash
nano /mnt/tank/sale-notificator/config/config.json
```

### Check Status
```bash
docker ps | grep sale-notificator
```

### Manual Price Check
```bash
docker exec sale-notificator python3 src/main.py
```

---

## ✅ Final Checklist

- [ ] Datasets created (`config` and `logs`)
- [ ] `config.json` created and edited
- [ ] Gmail App Password obtained
- [ ] Products added to track
- [ ] Schedule configured (default: 9 AM & 5 PM)
- [ ] Custom App deployed
- [ ] Container status is **Active** (green)
- [ ] Logs show successful startup
- [ ] Email test successful (optional)

---

## 🎉 Congratulations!

You now have an automated price tracker running on your TrueNAS server!

**What happens now:**
- Every day at 9 AM and 5 PM (or your custom schedule)
- App checks all your tracked products
- If any price drops below your threshold
- You get an email alert instantly
- All activity is logged for your review

**Enjoy automated price tracking!** 🎯📉📧

---

## 📚 Additional Resources

- **Configuration Guide:** See CONFIG.md in the repo
- **Cron Help:** https://crontab.guru
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Timezone List:** https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

---

## 🆘 Need Help?

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs: `docker logs sale-notificator`
3. Verify config is valid JSON: `cat config.json | python3 -m json.tool`
4. Check GitHub Issues: https://github.com/AntonRova/SaleNotificator2/issues

**Remember:** This app was built with AI assistance. Use at your own risk. See README for disclaimer.
