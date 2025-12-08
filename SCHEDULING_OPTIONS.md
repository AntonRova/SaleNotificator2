# Scheduling Options for SaleNotificator2

The application (`main.py`) is designed as a **run-once** script - it checks prices and exits. To run it regularly, you need a scheduler.

## Overview of Options

| Option | Complexity | Flexibility | Recommended For |
|--------|------------|-------------|-----------------|
| **1. Cron in Container** | Medium | High | Most users (TrueNAS) |
| **2. TrueNAS Cron Job** | Low | Medium | Users comfortable with TrueNAS CLI |
| **3. Python Daemon with Sleep** | High | Very High | Advanced users wanting custom logic |
| **4. External Orchestration** | Very High | Very High | Kubernetes/enterprise environments |

---

## Option 1: Cron Inside Container (Current Implementation) ✅

### How It Works

The Dockerfile includes a cron daemon that runs inside the container:

```dockerfile
# Default schedule: Every hour at :00 minutes
RUN echo "0 * * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"
```

### Current Schedule

**Hourly:** Runs at minute 0 of every hour (1:00 AM, 2:00 AM, ..., 11:00 PM, 12:00 AM)

### How to Customize the Schedule

Edit the `Dockerfile` line 24-27 and rebuild:

#### Examples

```dockerfile
# Every 30 minutes
RUN echo "*/30 * * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Every 2 hours
RUN echo "0 */2 * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Every 6 hours (4 times per day)
RUN echo "0 */6 * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Daily at 9:00 AM
RUN echo "0 9 * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Twice daily (9 AM and 9 PM)
RUN echo "0 9,21 * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Every Monday at 10:00 AM
RUN echo "0 10 * * 1 cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"

# Business hours: Every hour from 9 AM to 5 PM, Monday-Friday
RUN echo "0 9-17 * * 1-5 cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1"
```

#### After Editing

```bash
# Rebuild the image
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Pros
- ✅ Self-contained solution
- ✅ Portable (works anywhere Docker runs)
- ✅ No external dependencies
- ✅ Runs automatically on container start
- ✅ Perfect for TrueNAS Custom Apps

### Cons
- ❌ Requires image rebuild to change schedule
- ❌ Adds ~20MB to image (cron package)
- ❌ Container must stay running

---

## Option 2: TrueNAS Cron Job (External Scheduling)

Instead of cron inside the container, use TrueNAS's built-in cron to run the container on a schedule.

### How It Works

1. Container runs once and exits (no cron inside)
2. TrueNAS cron starts the container on schedule

### Modified Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY config.py .

RUN mkdir -p /app/config /app/logs

VOLUME ["/app/config", "/app/logs"]

# Just run the script once and exit
CMD ["python3", "src/main.py"]
```

### TrueNAS Setup

1. **In TrueNAS Web UI:**
   - Go to **System Settings** > **Advanced** > **Cron Jobs**
   - Click **Add**
   - **Description:** `Run Price Checker`
   - **Command:**
     ```bash
     docker start sale-notificator || docker run --rm \
       -v /mnt/your-pool/apps/sale-notificator/config:/app/config:ro \
       -v /mnt/your-pool/apps/sale-notificator/logs:/app/logs \
       --name sale-notificator \
       sale-notificator:latest
     ```
   - **Schedule:** Hourly (or custom)
   - **User:** `root`

2. **Or via SSH:**
   ```bash
   # Edit crontab
   crontab -e

   # Add line (runs every hour)
   0 * * * * docker start sale-notificator || docker run --rm -v /mnt/pool/apps/sale-notificator/config:/app/config:ro -v /mnt/pool/apps/sale-notificator/logs:/app/logs --name sale-notificator sale-notificator:latest
   ```

### Pros
- ✅ Very simple container (no cron dependency)
- ✅ Change schedule without rebuilding image
- ✅ Leverage TrueNAS's native scheduling
- ✅ Smaller image size

### Cons
- ❌ Requires TrueNAS SSH/CLI access
- ❌ Not portable to other systems
- ❌ More complex setup
- ❌ Can't use TrueNAS Custom App easily

---

## Option 3: Python Daemon with Sleep Loop

Convert the application to run continuously with configurable intervals.

### New File: `src/scheduler.py`

```python
#!/usr/bin/env python3
"""Scheduler daemon for continuous price checking."""

import time
import os
from main import main

# Get check interval from environment variable (default: 3600 = 1 hour)
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL_SECONDS', '3600'))

if __name__ == '__main__':
    print(f"Starting price checker daemon (checking every {CHECK_INTERVAL} seconds)")

    # Run immediately on startup
    main()

    # Then run on schedule
    while True:
        time.sleep(CHECK_INTERVAL)
        main()
```

### Modified Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY config.py .

RUN mkdir -p /app/config /app/logs

VOLUME ["/app/config", "/app/logs"]

# Run the scheduler daemon
CMD ["python3", "src/scheduler.py"]
```

### docker-compose.yml

```yaml
services:
  price-notificator:
    build: .
    environment:
      - CHECK_INTERVAL_SECONDS=3600  # 1 hour
      # - CHECK_INTERVAL_SECONDS=1800  # 30 minutes
      # - CHECK_INTERVAL_SECONDS=7200  # 2 hours
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
```

### Pros
- ✅ Change schedule with environment variable (no rebuild)
- ✅ Very flexible (can add custom logic)
- ✅ No cron dependency
- ✅ Simple to understand

### Cons
- ❌ Less precise than cron (slight drift over time)
- ❌ No built-in "at specific time" scheduling (9 AM daily, etc.)
- ❌ Requires code changes to application
- ❌ If container restarts, timing resets

---

## Option 4: Kubernetes CronJob or Docker Swarm

For enterprise/production environments.

### Example: Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: sale-notificator
spec:
  schedule: "0 * * * *"  # Every hour
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: price-checker
            image: sale-notificator:latest
            volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
            - name: logs
              mountPath: /app/logs
          restartPolicy: OnFailure
          volumes:
          - name: config
            persistentVolumeClaim:
              claimName: sale-notificator-config
          - name: logs
            persistentVolumeClaim:
              claimName: sale-notificator-logs
```

### Pros
- ✅ Enterprise-grade scheduling
- ✅ Built-in retry logic
- ✅ Resource management
- ✅ Monitoring and alerting integration

### Cons
- ❌ Requires Kubernetes cluster
- ❌ Significant complexity
- ❌ Overkill for simple use case

---

## Recommendation for TrueNAS Users

### For Most Users: **Option 1** (Current Implementation)

**Why:**
- Works out of the box
- No TrueNAS configuration needed
- Easy to deploy as Custom App
- Self-contained and portable

**When to change schedule:**
- Edit Dockerfile
- Rebuild image: `docker-compose build --no-cache`
- Restart: `docker-compose up -d`

### For Advanced Users Who Want Flexibility: **Option 3** (Python Daemon)

**Why:**
- Change schedule with environment variable
- No rebuild required
- Still self-contained

**Trade-off:**
- Less precise than cron
- Requires adding new Python file

---

## Cron Schedule Quick Reference

```
┌─── minute (0-59)
│ ┌─── hour (0-23)
│ │ ┌─── day of month (1-31)
│ │ │ ┌─── month (1-12)
│ │ │ │ ┌─── day of week (0-7, 0 and 7 are Sunday)
│ │ │ │ │
* * * * * command
```

### Common Patterns

| Schedule | Cron Expression |
|----------|----------------|
| Every hour | `0 * * * *` |
| Every 30 minutes | `*/30 * * * *` |
| Every 2 hours | `0 */2 * * *` |
| Every 6 hours | `0 */6 * * *` |
| Daily at midnight | `0 0 * * *` |
| Daily at 9 AM | `0 9 * * *` |
| Twice daily (9 AM, 9 PM) | `0 9,21 * * *` |
| Every weekday at 9 AM | `0 9 * * 1-5` |
| Every Monday at 10 AM | `0 10 * * 1` |
| First day of month at midnight | `0 0 1 * *` |

### Interval Equivalents

| Interval | Seconds | Cron |
|----------|---------|------|
| 15 minutes | 900 | `*/15 * * * *` |
| 30 minutes | 1800 | `*/30 * * * *` or `0,30 * * * *` |
| 1 hour | 3600 | `0 * * * *` |
| 2 hours | 7200 | `0 */2 * * *` |
| 6 hours | 21600 | `0 */6 * * *` |
| 12 hours | 43200 | `0 */12 * * *` |
| 24 hours | 86400 | `0 0 * * *` |

---

## Testing Your Schedule

### Test Cron Schedule

```bash
# View logs in real-time
docker logs -f sale-notificator

# Or check cron log specifically
docker exec sale-notificator tail -f /var/log/cron.log

# Or check application logs
tail -f /mnt/your-pool/apps/sale-notificator/logs/price_checks_*.log
```

### Manual Test Run

```bash
# Trigger a manual check without waiting for cron
docker exec sale-notificator python3 src/main.py
```

### Verify Cron is Running

```bash
# Check if cron daemon is running
docker exec sale-notificator ps aux | grep cron

# Check crontab
docker exec sale-notificator crontab -l
```

---

## Which Option Should You Choose?

### Choose **Option 1** (Cron in Container - Current) if:
- ✅ You're deploying to TrueNAS as a Custom App
- ✅ You want a self-contained solution
- ✅ You're okay rebuilding the image to change schedules
- ✅ You want "set it and forget it" operation

### Choose **Option 2** (TrueNAS Cron) if:
- ✅ You're comfortable with SSH/command line
- ✅ You want to change schedules without rebuilding
- ✅ You want the smallest possible container
- ✅ You only plan to run on TrueNAS

### Choose **Option 3** (Python Daemon) if:
- ✅ You want to change intervals via environment variables
- ✅ You want simple interval-based scheduling (not "at 9 AM daily")
- ✅ You're okay with slight timing drift
- ✅ You want maximum flexibility without rebuilds

### Choose **Option 4** (Kubernetes) if:
- ✅ You're already running Kubernetes
- ✅ You need enterprise features (retries, monitoring, etc.)
- ✅ You have multiple applications to orchestrate

---

## My Recommendation

**Stick with Option 1** (what's already implemented) because:

1. It works perfectly for TrueNAS Custom Apps
2. Self-contained and portable
3. Precise scheduling with cron
4. Industry-standard approach
5. Easy to deploy and maintain

If you need to change the schedule frequently, we can implement **Option 3** (Python daemon with environment variables).

**What schedule do you want?** I can help you customize it!
