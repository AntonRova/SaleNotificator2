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

# Copy example config file to templates directory
COPY config/config.example.json /app/templates/

# Create necessary directories
RUN mkdir -p /app/config /app/logs /app/templates && \
    chmod 755 /app/logs

# Create entrypoint script with config validation and auto-deployment
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "SaleNotificator2 Docker Container Starting..."\n\
echo "Configuration directory: /app/config"\n\
echo "Logs directory: /app/logs"\n\
echo ""\n\
\n\
# Auto-deploy template config if no config exists\n\
if [ ! -f "/app/config/config.json" ]; then\n\
    echo "No configuration found. Deploying template config.json..."\n\
    cp /app/templates/config.example.json /app/config/config.json\n\
    echo ""\n\
    echo "✓ Template configuration file deployed to /app/config/config.json"\n\
    echo ""\n\
    echo "IMPORTANT: Edit /app/config/config.json with your settings:"\n\
    echo "  - Email SMTP settings"\n\
    echo "  - Schedule (cron expression)"\n\
    echo "  - Tracked items (products to monitor)"\n\
    echo ""\n\
    echo "After editing config, restart the container."\n\
    echo ""\n\
else\n\
    echo "✓ Found config.json"\n\
    echo ""\n\
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
HEALTHCHECK --interval=30s --timeout=10s --start-period=1m --retries=3 \
    CMD pgrep -f "python.*scheduler" > /dev/null || exit 1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
