# Quick Start Guide - TrueNAS Deployment

This guide will get you up and running in **5 minutes** using the automated setup script.

## Option 1: Automated Setup (Recommended) 🚀

### Step 1: Download and Run Setup Script

SSH into your TrueNAS server and run:

```bash
# Download the setup script
curl -O https://raw.githubusercontent.com/AntonRova/SaleNotificator2/claude/docker-truenas-setup-0144QCmGtmmnf5Syv1GLrYbi/setup-truenas.sh

# Make it executable
chmod +x setup-truenas.sh

# Run the setup
./setup-truenas.sh
```

**Or, if you already cloned the repo:**

```bash
cd /path/to/SaleNotificator2
./setup-truenas.sh
```

### Step 2: Follow the Interactive Prompts

The script will ask you for:

1. **Installation Path**: Where to install (e.g., `/mnt/tank/apps/sale-notificator`)
2. **Email Settings**: SMTP server, sender email, password
3. **Schedule**: Choose from presets or enter custom cron
4. **Products**: Optionally add a product to track

Example interaction:
```
Enter installation path: /mnt/tank/apps/sale-notificator
SMTP Server [smtp.gmail.com]: (press Enter for Gmail)
Sender Email Address: myemail@gmail.com
Password: ****************
Select schedule [4]: 4 (for 9 AM and 5 PM)
Timezone [America/New_York]: (press Enter or type yours)
```

### Step 3: Deploy to TrueNAS

After the script completes, deploy as Custom App:

1. Open TrueNAS Web UI → **Apps** → **Discover Apps** → **Custom App**

2. Fill in these fields:
   - **Application Name**: `sale-notificator`
   - **Image Repository**: `sale-notificator`
   - **Image Tag**: `latest`
   - **Image Pull Policy**: `IfNotPresent`

3. **Environment Variables** - Add one:
   - `TZ` = `America/New_York` (or your timezone)

4. **Storage** - Add TWO volumes:

   **Volume 1 (Config):**
   - Mount Path: `/app/config`
   - Host Path: `/mnt/tank/apps/sale-notificator/config` (use your path)
   - ✅ **Read Only**: CHECK THIS

   **Volume 2 (Logs):**
   - Mount Path: `/app/logs`
   - Host Path: `/mnt/tank/apps/sale-notificator/logs` (use your path)
   - ☐ **Read Only**: LEAVE UNCHECKED

5. Click **Install**

### Step 4: Verify It's Working

Check the logs:
```bash
docker logs sale-notificator
```

You should see:
```
✓ Found unified config.json
Schedule: Twice daily at 9 AM and 5 PM
Cron expression: 0 9,17 * * *
Starting STARTUP check #1...
```

---

## Option 2: Manual Setup

See [TRUENAS_DEPLOYMENT.md](TRUENAS_DEPLOYMENT.md) for detailed manual setup instructions.

---

## What the Setup Script Does

The automated script handles:
- ✅ Creates directory structure (`/config`, `/logs`, `/app`)
- ✅ Clones the repository
- ✅ Creates `config.json` with your settings
- ✅ Sets proper permissions (chmod 600 for config)
- ✅ Builds the Docker image

**Time saved:** ~10-15 minutes compared to manual setup!

---

## Schedule Options in Setup Script

When prompted, choose from:

| Option | Schedule | Cron Expression |
|--------|----------|-----------------|
| 1 | Every hour | `0 * * * *` |
| 2 | Every 2 hours | `0 */2 * * *` |
| 3 | Every 6 hours | `0 */6 * * *` |
| 4 | **Twice daily (9 AM & 5 PM)** | `0 9,17 * * *` |
| 5 | Daily at 9 AM | `0 9 * * *` |
| 6 | Business hours (9-5, M-F) | `0 9-17 * * 1-5` |
| 7 | Custom | Enter your own |

**Recommended:** Option 4 (twice daily)

---

## After Setup

### Editing Configuration

```bash
nano /mnt/tank/apps/sale-notificator/config/config.json
```

Change the schedule, add more products, update email settings, etc.

**Apply changes:**
```bash
docker restart sale-notificator
```

No rebuild needed! ✨

### Adding More Products

Edit your config:
```bash
nano /mnt/tank/apps/sale-notificator/config/config.json
```

Add to the `tracked_items` array:
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

Restart:
```bash
docker restart sale-notificator
```

### Viewing Logs

**Container logs:**
```bash
docker logs -f sale-notificator
```

**Application logs:**
```bash
tail -f /mnt/tank/apps/sale-notificator/logs/*.log
```

### Changing Schedule

Edit config:
```bash
nano /mnt/tank/apps/sale-notificator/config/config.json
```

Change the cron expression:
```json
{
  "schedule": {
    "cron": "0 */6 * * *"  // Every 6 hours instead
  }
}
```

Restart:
```bash
docker restart sale-notificator
```

---

## Common Timezones

Update in your config.json:

```json
{
  "schedule": {
    "timezone": "America/New_York"
  }
}
```

Common options:
- `America/New_York` - Eastern
- `America/Chicago` - Central
- `America/Denver` - Mountain
- `America/Los_Angeles` - Pacific
- `Europe/London` - UK
- `Europe/Paris` - Central Europe
- `Asia/Tokyo` - Japan
- `Australia/Sydney` - Australia
- `Pacific/Auckland` - New Zealand

---

## Troubleshooting

### Setup Script Fails

**Problem:** Permission denied
```bash
# Run as root or with sudo
sudo ./setup-truenas.sh
```

**Problem:** Git not found
```bash
# TrueNAS should have git by default, but if not:
pkg install git
```

### Container Won't Start

**Check logs:**
```bash
docker logs sale-notificator
```

**Common issues:**
- Invalid JSON in config (use `python -m json.tool < config.json` to validate)
- Wrong volume paths
- Invalid cron expression

### Email Not Sending

1. For Gmail, use App Password: https://myaccount.google.com/apppasswords
2. Check `sender_email` is not the placeholder `your_email@gmail.com`
3. Verify firewall allows outbound port 587

---

## Need More Help?

- **Full deployment guide:** [TRUENAS_DEPLOYMENT.md](TRUENAS_DEPLOYMENT.md)
- **Configuration reference:** [CONFIG.md](CONFIG.md)
- **Scheduling options:** [SCHEDULING_OPTIONS.md](SCHEDULING_OPTIONS.md)

---

## What's Next?

Once deployed:
1. ✅ Container runs automatically
2. ✅ Checks prices at scheduled times (e.g., 9 AM and 5 PM)
3. ✅ Sends email alerts when prices drop below threshold
4. ✅ Logs all activity to monthly files
5. ✅ Restarts automatically if it crashes

**That's it!** You're now tracking prices on TrueNAS! 🎉
