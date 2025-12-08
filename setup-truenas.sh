#!/bin/bash
#
# TrueNAS SCALE Automated Setup Script for SaleNotificator2
#
# This script automates the initial setup process:
#   1. Creates necessary directories
#   2. Clones the repository
#   3. Creates config.json with interactive prompts
#   4. Sets proper permissions
#   5. Builds the Docker image
#
# Usage:
#   curl -O https://raw.githubusercontent.com/AntonRova/SaleNotificator2/claude/docker-truenas-setup-0144QCmGtmmnf5Syv1GLrYbi/setup-truenas.sh
#   chmod +x setup-truenas.sh
#   ./setup-truenas.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Banner
clear
echo -e "${GREEN}"
cat << "EOF"
 ____        _      _   _       _   _  __ _           _             ____
/ ___|  __ _| | ___| \ | | ___ | |_(_)/ _(_) ___ __ _| |_ ___  _ __|___ \
\___ \ / _` | |/ _ \  \| |/ _ \| __| | |_| |/ __/ _` | __/ _ \| '__|__) |
 ___) | (_| | |  __/ |\  | (_) | |_| |  _| | (_| (_| | || (_) | |  / __/
|____/ \__,_|_|\___|_| \_|\___/ \__|_|_| |_|\___\__,_|\__\___/|_| |_____|

         TrueNAS SCALE Automated Setup Script
EOF
echo -e "${NC}"

print_info "This script will help you set up SaleNotificator2 on TrueNAS SCALE"
echo ""

# Step 1: Get installation path
print_header "Step 1: Installation Location"

echo "Where do you want to install the application?"
echo "This should be a path on your TrueNAS pool."
echo ""
echo "Examples:"
echo "  - /mnt/tank/apps/sale-notificator"
echo "  - /mnt/main-pool/apps/sale-notificator"
echo "  - /mnt/data/sale-notificator"
echo ""

read -p "Enter installation path: " INSTALL_PATH

# Validate path
if [[ ! "$INSTALL_PATH" =~ ^/mnt/ ]]; then
    print_warning "Path doesn't start with /mnt/ - are you sure this is correct?"
    read -p "Continue anyway? (y/n): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled"
        exit 1
    fi
fi

print_info "Installation path: $INSTALL_PATH"
echo ""

# Step 2: Create directories
print_header "Step 2: Creating Directories"

mkdir -p "$INSTALL_PATH"/{config,logs,app}
print_success "Created directory structure"

ls -la "$INSTALL_PATH"
echo ""

# Step 3: Clone repository
print_header "Step 3: Downloading Application"

cd "$INSTALL_PATH/app"

if [ -d ".git" ]; then
    print_info "Repository already exists, pulling latest changes..."
    git pull
else
    print_info "Cloning repository..."
    git clone https://github.com/AntonRova/SaleNotificator2.git .
fi

print_info "Checking out correct branch..."
git checkout claude/docker-truenas-setup-0144QCmGtmmnf5Syv1GLrYbi

print_success "Application code downloaded"
echo ""

# Step 4: Interactive config creation
print_header "Step 4: Configuration Setup"

CONFIG_FILE="$INSTALL_PATH/config/config.json"

if [ -f "$CONFIG_FILE" ]; then
    print_warning "Config file already exists at: $CONFIG_FILE"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        print_info "Keeping existing config file"
        SKIP_CONFIG=true
    fi
fi

if [ "$SKIP_CONFIG" != "true" ]; then
    echo ""
    echo "Let's set up your configuration..."
    echo ""

    # Email configuration
    echo -e "${BLUE}--- Email Configuration ---${NC}"
    echo ""

    read -p "SMTP Server [smtp.gmail.com]: " SMTP_SERVER
    SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}

    read -p "SMTP Port [587]: " SMTP_PORT
    SMTP_PORT=${SMTP_PORT:-587}

    read -p "Sender Email Address: " SENDER_EMAIL
    while [ -z "$SENDER_EMAIL" ]; do
        print_error "Sender email is required"
        read -p "Sender Email Address: " SENDER_EMAIL
    done

    echo ""
    print_info "For Gmail, use an App Password (not your regular password)"
    print_info "Generate one at: https://myaccount.google.com/apppasswords"
    echo ""
    read -sp "Sender Email Password/App Password: " SENDER_PASSWORD
    echo ""
    while [ -z "$SENDER_PASSWORD" ]; do
        print_error "Password is required"
        read -sp "Sender Email Password/App Password: " SENDER_PASSWORD
        echo ""
    done

    read -p "Recipient Email Address [$SENDER_EMAIL]: " RECIPIENT_EMAIL
    RECIPIENT_EMAIL=${RECIPIENT_EMAIL:-$SENDER_EMAIL}

    echo ""
    echo -e "${BLUE}--- Schedule Configuration ---${NC}"
    echo ""
    echo "Select a schedule preset or enter custom cron expression:"
    echo ""
    echo "1) Every hour (0 * * * *)"
    echo "2) Every 2 hours (0 */2 * * *)"
    echo "3) Every 6 hours (0 */6 * * *)"
    echo "4) Twice daily at 9 AM and 5 PM (0 9,17 * * *)"
    echo "5) Daily at 9 AM (0 9 * * *)"
    echo "6) Business hours (9 AM-5 PM, Mon-Fri) (0 9-17 * * 1-5)"
    echo "7) Custom cron expression"
    echo ""
    read -p "Select option [4]: " SCHEDULE_OPTION
    SCHEDULE_OPTION=${SCHEDULE_OPTION:-4}

    case $SCHEDULE_OPTION in
        1)
            CRON_EXPRESSION="0 * * * *"
            SCHEDULE_DESC="Every hour"
            ;;
        2)
            CRON_EXPRESSION="0 */2 * * *"
            SCHEDULE_DESC="Every 2 hours"
            ;;
        3)
            CRON_EXPRESSION="0 */6 * * *"
            SCHEDULE_DESC="Every 6 hours"
            ;;
        4)
            CRON_EXPRESSION="0 9,17 * * *"
            SCHEDULE_DESC="Twice daily at 9 AM and 5 PM"
            ;;
        5)
            CRON_EXPRESSION="0 9 * * *"
            SCHEDULE_DESC="Daily at 9 AM"
            ;;
        6)
            CRON_EXPRESSION="0 9-17 * * 1-5"
            SCHEDULE_DESC="Business hours (9 AM-5 PM, Mon-Fri)"
            ;;
        7)
            read -p "Enter custom cron expression: " CRON_EXPRESSION
            read -p "Enter schedule description: " SCHEDULE_DESC
            ;;
        *)
            CRON_EXPRESSION="0 9,17 * * *"
            SCHEDULE_DESC="Twice daily at 9 AM and 5 PM"
            ;;
    esac

    print_info "Schedule: $SCHEDULE_DESC ($CRON_EXPRESSION)"
    echo ""

    read -p "Timezone [America/New_York]: " TIMEZONE
    TIMEZONE=${TIMEZONE:-America/New_York}

    echo ""
    echo -e "${BLUE}--- Product Tracking ---${NC}"
    echo ""
    print_info "You can add products to track now or edit the config file later"
    echo ""
    read -p "Add a product to track now? (y/n) [n]: " ADD_PRODUCT

    if [[ "$ADD_PRODUCT" =~ ^[Yy]$ ]]; then
        read -p "Product Name: " PRODUCT_NAME
        read -p "Product URL: " PRODUCT_URL
        read -p "CSS Selector for price [.price]: " CSS_SELECTOR
        CSS_SELECTOR=${CSS_SELECTOR:-.price}
        read -p "Price Threshold (alert when below): " THRESHOLD
        read -p "Currency [USD]: " CURRENCY
        CURRENCY=${CURRENCY:-USD}

        TRACKED_ITEMS=$(cat <<EOF
    {
      "name": "$PRODUCT_NAME",
      "url": "$PRODUCT_URL",
      "parameter": "price",
      "css_selector": "$CSS_SELECTOR",
      "threshold": $THRESHOLD,
      "currency": "$CURRENCY",
      "enabled": true
    }
EOF
)
    else
        TRACKED_ITEMS=$(cat <<EOF
    {
      "name": "Example Product - Edit Me",
      "url": "https://example.com/product",
      "parameter": "price",
      "css_selector": ".price",
      "threshold": 99.99,
      "currency": "USD",
      "enabled": false
    }
EOF
)
    fi

    # Create config.json
    print_info "Creating configuration file..."

    cat > "$CONFIG_FILE" <<EOF
{
  "email": {
    "smtp_server": "$SMTP_SERVER",
    "smtp_port": $SMTP_PORT,
    "sender_email": "$SENDER_EMAIL",
    "sender_password": "$SENDER_PASSWORD",
    "recipient_email": "$RECIPIENT_EMAIL",
    "use_tls": true
  },
  "schedule": {
    "enabled": true,
    "cron": "$CRON_EXPRESSION",
    "timezone": "$TIMEZONE",
    "run_on_startup": true,
    "description": "$SCHEDULE_DESC"
  },
  "tracked_items": [
$TRACKED_ITEMS
  ]
}
EOF

    print_success "Configuration file created at: $CONFIG_FILE"
fi

echo ""

# Step 5: Set permissions
print_header "Step 5: Setting Permissions"

chmod 600 "$CONFIG_FILE"
chmod 755 "$INSTALL_PATH/config"
chmod 755 "$INSTALL_PATH/logs"

print_success "Permissions set"
ls -la "$INSTALL_PATH/config/"
echo ""

# Step 6: Build Docker image
print_header "Step 6: Building Docker Image"

cd "$INSTALL_PATH/app"
print_info "This may take 2-3 minutes..."
echo ""

docker build -t sale-notificator:latest .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

echo ""

# Verify image
print_info "Verifying Docker image..."
docker images | grep sale-notificator
echo ""

# Summary
print_header "Setup Complete! 🎉"

echo -e "${GREEN}Installation Summary:${NC}"
echo ""
echo "  Installation Path:  $INSTALL_PATH"
echo "  Config File:        $INSTALL_PATH/config/config.json"
echo "  Logs Directory:     $INSTALL_PATH/logs"
echo "  Application Code:   $INSTALL_PATH/app"
echo "  Docker Image:       sale-notificator:latest"
echo "  Schedule:           $SCHEDULE_DESC"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Review your configuration:"
echo "   nano $INSTALL_PATH/config/config.json"
echo ""
echo "2. Deploy as TrueNAS Custom App:"
echo "   - Go to Apps > Discover Apps > Custom App"
echo "   - Application Name: sale-notificator"
echo "   - Image Repository: sale-notificator"
echo "   - Image Tag: latest"
echo "   - Add volume mounts:"
echo "     • Host: $INSTALL_PATH/config → Container: /app/config (READ ONLY)"
echo "     • Host: $INSTALL_PATH/logs → Container: /app/logs"
echo "   - Add environment variable:"
echo "     • TZ = $TIMEZONE"
echo ""
echo "3. Or run with docker-compose:"
echo "   cd $INSTALL_PATH/app"
echo "   # Edit docker-compose.yml to update paths"
echo "   docker-compose up -d"
echo ""

echo -e "${YELLOW}Important:${NC}"
echo "  • Your config contains sensitive information (passwords)"
echo "  • Keep it secure and backed up"
echo "  • To change schedule: edit config.json and restart container"
echo ""

print_success "Setup script completed successfully!"
echo ""
echo "For detailed deployment instructions, see:"
echo "  $INSTALL_PATH/app/TRUENAS_DEPLOYMENT.md"
echo ""
