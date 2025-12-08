# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install cron for scheduled execution
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ src/
COPY config.py .

# Create necessary directories
RUN mkdir -p /app/config /app/logs && \
    chmod 755 /app/logs

# Create cron job to run hourly
RUN echo "0 * * * * cd /app && /usr/local/bin/python3 src/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/price-checker && \
    chmod 0644 /etc/cron.d/price-checker && \
    crontab /etc/cron.d/price-checker && \
    touch /var/log/cron.log

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "SaleNotificator2 Docker Container Starting..."\n\
echo "Configuration directory: /app/config"\n\
echo "Logs directory: /app/logs"\n\
echo ""\n\
\n\
# Check if config files exist\n\
if [ ! -f "/app/config/tracked_items.json" ]; then\n\
    echo "ERROR: /app/config/tracked_items.json not found!"\n\
    echo "Please mount your config directory with tracked_items.json"\n\
    exit 1\n\
fi\n\
\n\
if [ ! -f "/app/config/email_config.json" ]; then\n\
    echo "ERROR: /app/config/email_config.json not found!"\n\
    echo "Please mount your config directory with email_config.json"\n\
    exit 1\n\
fi\n\
\n\
echo "Configuration files found ✓"\n\
echo ""\n\
\n\
# Run once immediately on startup\n\
echo "Running initial price check..."\n\
/usr/local/bin/python3 src/main.py\n\
echo ""\n\
echo "Initial check complete. Cron will run hourly checks."\n\
echo "Cron schedule: Every hour (0 * * * *)"\n\
echo ""\n\
\n\
# Start cron in foreground\n\
echo "Starting cron daemon..."\n\
cron && tail -f /var/log/cron.log /app/logs/*.log\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expose volumes for configuration and logs
VOLUME ["/app/config", "/app/logs"]

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
