# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

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

# Create entrypoint script with config validation
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "SaleNotificator2 Docker Container Starting..."\n\
echo "Configuration directory: /app/config"\n\
echo "Logs directory: /app/logs"\n\
echo ""\n\
\n\
# Check if unified config exists\n\
if [ -f "/app/config/config.json" ]; then\n\
    echo "✓ Found unified config.json"\n\
    echo "  Schedule will be read from config.json"\n\
    echo ""\n\
elif [ -f "/app/config/tracked_items.json" ] && [ -f "/app/config/email_config.json" ]; then\n\
    echo "✓ Found legacy config files (tracked_items.json + email_config.json)"\n\
    echo "  WARNING: Schedule control requires unified config.json"\n\
    echo "  Using default hourly schedule (0 * * * *)"\n\
    echo "  Consider migrating to config.json for schedule customization"\n\
    echo ""\n\
else\n\
    echo "ERROR: Configuration files not found!"\n\
    echo ""\n\
    echo "Please provide ONE of the following:"\n\
    echo "  1. Unified config:  /app/config/config.json (recommended)"\n\
    echo "  2. Legacy configs:  /app/config/tracked_items.json"\n\
    echo "                      /app/config/email_config.json"\n\
    echo ""\n\
    echo "See config.example.json for the unified config format"\n\
    exit 1\n\
fi\n\
\n\
# Start the scheduler daemon\n\
echo "Starting scheduler daemon..."\n\
echo ""\n\
exec /usr/local/bin/python3 -u src/scheduler.py\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expose volumes for configuration and logs
VOLUME ["/app/config", "/app/logs"]

# Health check (ensure scheduler is running)
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f scheduler.py || exit 1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
