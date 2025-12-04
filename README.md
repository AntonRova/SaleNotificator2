# SaleNotificator2

A sale notification system that monitors products and sends email notifications when discounts are detected.

## Configuration

All configuration is managed through a single `config.json` file. Copy the example configuration to get started:

```bash
cp config.example.json config.json
```

Then edit `config.json` with your settings.

### Configuration Sections

#### Email Settings

| Setting | Description |
|---------|-------------|
| `smtp_server` | SMTP server address (e.g., smtp.gmail.com) |
| `smtp_port` | SMTP server port (usually 587 for TLS) |
| `sender_email` | Email address to send notifications from |
| `sender_password` | App password for the sender email |
| `recipient_emails` | List of email addresses to receive notifications |
| `use_tls` | Whether to use TLS encryption (recommended: true) |

#### Notification Settings

| Setting | Description |
|---------|-------------|
| `enabled` | Enable or disable notifications |
| `min_discount_percent` | Minimum discount percentage to trigger a notification |
| `check_interval_minutes` | How often to check for sales (in minutes) |

#### Logging Settings

| Setting | Description |
|---------|-------------|
| `level` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `file` | Log file path |

## Usage

```python
from config import get_config

# Get configuration instance
config = get_config()

# Access email settings
print(config.smtp_server)
print(config.sender_email)

# Access using dot notation
smtp_port = config.get("email.smtp_port")

# Access notification settings
if config.notifications_enabled:
    print(f"Checking for discounts >= {config.min_discount_percent}%")
```
