# TrueNAS 24.10 Deployment Guide

This guide will walk you through deploying SaleNotificator2 as a Docker container on TrueNAS SCALE 24.10.

## Prerequisites

- TrueNAS SCALE 24.10 or later
- Basic familiarity with TrueNAS interface
- Docker/container knowledge (helpful but not required)

## Deployment Options

There are two ways to deploy this application on TrueNAS:

1. **Custom App (Recommended)** - Use TrueNAS's built-in Custom App feature
2. **Docker Compose** - Use docker-compose via SSH

---

## Option 1: Deploy as TrueNAS Custom App (Recommended)

### Step 1: Prepare Your Dataset

1. Open TrueNAS web interface
2. Go to **Datasets** (Storage menu)
3. Create a new dataset for the application:
   - Name: `apps/sale-notificator`
   - Create two subdirectories:
     - `config` - for configuration files
     - `logs` - for application logs

### Step 2: Create Configuration Files

1. Navigate to your dataset: `/mnt/your-pool/apps/sale-notificator/config/`

2. Create `tracked_items.json`:
   ```json
   {
     "items": [
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

3. Create `email_config.json`:
   ```json
   {
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "sender_email": "your-email@gmail.com",
     "sender_password": "your-app-password",
     "recipient_email": "recipient@example.com",
     "use_tls": true
   }
   ```

   **Note for Gmail users:**
   - Enable 2-factor authentication on your Google account
   - Generate an App Password: https://myaccount.google.com/apppasswords
   - Use the app password (not your regular password)

4. Set proper permissions:
   ```bash
   chmod 600 /mnt/your-pool/apps/sale-notificator/config/*.json
   ```

### Step 3: Build the Docker Image

You have two options to get the Docker image:

#### Option A: Build Locally on TrueNAS (Recommended)

1. SSH into your TrueNAS server
2. Clone or copy this repository to TrueNAS
3. Navigate to the project directory
4. Build the image:
   ```bash
   docker build -t sale-notificator:latest .
   ```

#### Option B: Build on Another Machine and Import

1. Build on your development machine:
   ```bash
   docker build -t sale-notificator:latest .
   docker save sale-notificator:latest -o sale-notificator.tar
   ```

2. Copy to TrueNAS:
   ```bash
   scp sale-notificator.tar user@truenas-ip:/mnt/your-pool/temp/
   ```

3. SSH into TrueNAS and import:
   ```bash
   docker load -i /mnt/your-pool/temp/sale-notificator.tar
   ```

### Step 4: Deploy as Custom App

1. In TrueNAS web UI, go to **Apps**
2. Click **Discover Apps**
3. Click **Custom App** button (top right)
4. Fill in the configuration:

#### Application Configuration

- **Application Name**: `sale-notificator`
- **Image Repository**: `sale-notificator`
- **Image Tag**: `latest`
- **Image Pull Policy**: `IfNotPresent`

#### Container Environment Variables

Add the following environment variable:
- **Variable Name**: `TZ`
- **Value**: `America/New_York` (or your timezone)

#### Storage Configuration

Click **Add** under "Storage" twice to add two host path volumes:

**Volume 1 (Config):**
- **Type**: Host Path
- **Host Path**: `/mnt/your-pool/apps/sale-notificator/config`
- **Mount Path**: `/app/config`
- **Read Only**: ✓ (Check this box for security)

**Volume 2 (Logs):**
- **Type**: Host Path
- **Host Path**: `/mnt/your-pool/apps/sale-notificator/logs`
- **Mount Path**: `/app/logs`
- **Read Only**: ☐ (Leave unchecked)

#### Resource Limits (Optional but Recommended)

- **CPU Limit**: `0.5` (cores)
- **Memory Limit**: `256` (MiB)

#### Restart Policy

- **Restart Policy**: `Unless Stopped`

5. Click **Install** and wait for the container to start

### Step 5: Verify Deployment

1. Go to **Apps** > **Installed**
2. Click on `sale-notificator`
3. Check **Logs** to verify:
   - Configuration files are found
   - Initial price check ran successfully
   - No errors in the logs

4. Check the logs directory:
   ```bash
   ls -lh /mnt/your-pool/apps/sale-notificator/logs/
   ```
   You should see a file like `price_checks_2024-12.log`

---

## Option 2: Deploy with Docker Compose via SSH

### Step 1: Prepare Directories and Config Files

Follow **Steps 1-2** from Option 1 above.

### Step 2: Update docker-compose.yml

1. Edit `docker-compose.yml` and update the volume paths:
   ```yaml
   volumes:
     - /mnt/your-pool/apps/sale-notificator/config:/app/config:ro
     - /mnt/your-pool/apps/sale-notificator/logs:/app/logs
   ```

2. Update the timezone if needed:
   ```yaml
   environment:
     - TZ=America/New_York  # Your timezone
   ```

### Step 3: Deploy

1. Copy the entire repository to TrueNAS:
   ```bash
   scp -r SaleNotificator2/ user@truenas-ip:/mnt/your-pool/apps/
   ```

2. SSH into TrueNAS:
   ```bash
   ssh user@truenas-ip
   cd /mnt/your-pool/apps/SaleNotificator2
   ```

3. Start the container:
   ```bash
   docker-compose up -d
   ```

4. Check logs:
   ```bash
   docker-compose logs -f
   ```

### Managing the Container

```bash
# Stop the container
docker-compose stop

# Start the container
docker-compose start

# Restart the container
docker-compose restart

# View logs
docker-compose logs -f

# Stop and remove container
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

---

## Schedule and Operation

### How It Works

- The container runs **hourly** automatically using cron
- Schedule: At minute 0 of every hour (e.g., 1:00, 2:00, 3:00, etc.)
- On startup, it runs an immediate check, then continues hourly
- All logs are written to monthly rotating files: `price_checks_YYYY-MM.log`

### Customizing the Schedule

To change the cron schedule, you'll need to modify the Dockerfile:

```dockerfile
# Current: Every hour
RUN echo "0 * * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Examples:
# Every 30 minutes:
RUN echo "*/30 * * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Every 6 hours:
RUN echo "0 */6 * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Daily at 9 AM:
RUN echo "0 9 * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"
```

Then rebuild the image:
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Monitoring and Troubleshooting

### View Real-Time Logs

**Option 1 users (Custom App):**
1. Go to Apps > Installed > sale-notificator
2. Click "Logs" button

**Option 2 users (Docker Compose):**
```bash
docker-compose logs -f
```

### Check Application Logs

View the monthly log files directly:
```bash
tail -f /mnt/your-pool/apps/sale-notificator/logs/price_checks_*.log
```

### Manual Test Run

Execute a manual price check:
```bash
docker exec sale-notificator python3 src/main.py
```

### Common Issues

#### "Config files not found"
- Verify files exist in `/mnt/your-pool/apps/sale-notificator/config/`
- Check file names are exactly: `tracked_items.json` and `email_config.json`
- Verify volume mounts are correct

#### "Email not sending"
- Check SMTP credentials in `email_config.json`
- For Gmail: Ensure you're using an App Password, not your account password
- Verify `use_tls: true` is set
- Check firewall allows outbound connection on port 587

#### "Price not found"
- CSS selector may be incorrect
- Website may have changed their HTML structure
- Cloudflare/anti-bot protection may be blocking
- Use `find_amazon_selector.py` to discover correct selectors

#### Container keeps restarting
- Check logs for errors
- Verify config JSON files are valid JSON (use a JSON validator)
- Check permissions on mounted directories

---

## Security Best Practices

1. **Protect Config Files**:
   ```bash
   chmod 600 /mnt/your-pool/apps/sale-notificator/config/*.json
   ```

2. **Mount Config as Read-Only**: The config volume should always be mounted as `:ro`

3. **Use App Passwords**: For Gmail and other providers, use app-specific passwords

4. **Regular Updates**: Periodically rebuild the image to get security updates:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

5. **Backup Configuration**: Regularly backup your `config/` directory

---

## Updating the Application

### Update Code

1. Pull latest changes (if using git):
   ```bash
   cd /mnt/your-pool/apps/SaleNotificator2
   git pull
   ```

2. Rebuild the image:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Update Configuration

Simply edit the JSON files in the config directory:
```bash
nano /mnt/your-pool/apps/sale-notificator/config/tracked_items.json
```

The changes will be picked up on the next scheduled run (no restart needed).

---

## Backup and Restore

### Backup

```bash
# Backup config files
tar -czf sale-notificator-backup-$(date +%Y%m%d).tar.gz \
  /mnt/your-pool/apps/sale-notificator/config

# Optionally backup logs
tar -czf sale-notificator-logs-$(date +%Y%m%d).tar.gz \
  /mnt/your-pool/apps/sale-notificator/logs
```

### Restore

```bash
# Restore config
tar -xzf sale-notificator-backup-YYYYMMDD.tar.gz -C /
```

---

## Uninstalling

### Option 1 (Custom App)
1. Go to Apps > Installed
2. Click on `sale-notificator`
3. Click **Delete**
4. Optionally delete the dataset

### Option 2 (Docker Compose)
```bash
cd /mnt/your-pool/apps/SaleNotificator2
docker-compose down
docker rmi sale-notificator:latest
```

Optionally delete the files:
```bash
rm -rf /mnt/your-pool/apps/sale-notificator
```

---

## Support

For issues or questions:
- Check application logs first
- Review this deployment guide
- Check the main README.md for application-specific help
- Verify your TrueNAS version is 24.10 or later

---

## Advanced: Multi-Instance Deployment

You can run multiple instances to track different sets of products:

1. Create separate datasets for each instance
2. Deploy multiple containers with different names
3. Each instance has its own config and logs

Example for a second instance:
```bash
# Create new dataset
/mnt/your-pool/apps/sale-notificator-instance2/

# Deploy with different name
docker run -d \
  --name sale-notificator-2 \
  -v /mnt/your-pool/apps/sale-notificator-instance2/config:/app/config:ro \
  -v /mnt/your-pool/apps/sale-notificator-instance2/logs:/app/logs \
  sale-notificator:latest
```

---

## Timezone Reference

Common timezones for the `TZ` environment variable:

- `America/New_York` - Eastern Time
- `America/Chicago` - Central Time
- `America/Denver` - Mountain Time
- `America/Los_Angeles` - Pacific Time
- `Europe/London` - UK
- `Europe/Paris` - Central European Time
- `Asia/Tokyo` - Japan
- `Australia/Sydney` - Australian Eastern Time
- `Pacific/Auckland` - New Zealand

Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
