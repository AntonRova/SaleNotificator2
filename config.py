"""
Configuration module for SaleNotificator2.

This module provides a unified configuration system using config.json.
Email and other settings are all managed in a single configuration file.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default configuration file path
CONFIG_FILE = Path(__file__).parent / "config.json"


class Config:
    """Configuration manager for SaleNotificator2."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the config.json file. Defaults to config.json
                        in the same directory as this module.
        """
        self.config_path = config_path or CONFIG_FILE
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from the JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please create a config.json file based on config.example.json"
            )

        with open(self.config_path, "r") as f:
            self._config = json.load(f)

    def save(self) -> None:
        """Save the current configuration to the JSON file."""
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Supports dot notation for nested keys (e.g., 'email.smtp_server').

        Args:
            key: The configuration key (supports dot notation).
            default: Default value if key is not found.

        Returns:
            The configuration value or the default.
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key.

        Supports dot notation for nested keys (e.g., 'email.smtp_server').

        Args:
            key: The configuration key (supports dot notation).
            value: The value to set.
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    # Email configuration properties
    @property
    def email(self) -> Dict[str, Any]:
        """Get the email configuration section."""
        return self._config.get("email", {})

    @property
    def smtp_server(self) -> str:
        """Get the SMTP server address."""
        return self.get("email.smtp_server", "smtp.gmail.com")

    @property
    def smtp_port(self) -> int:
        """Get the SMTP server port."""
        return self.get("email.smtp_port", 587)

    @property
    def sender_email(self) -> str:
        """Get the sender email address."""
        return self.get("email.sender_email", "")

    @property
    def sender_password(self) -> str:
        """Get the sender email password."""
        return self.get("email.sender_password", "")

    @property
    def recipient_emails(self) -> List[str]:
        """Get the list of recipient email addresses."""
        return self.get("email.recipient_emails", [])

    @property
    def use_tls(self) -> bool:
        """Check if TLS should be used for email."""
        return self.get("email.use_tls", True)

    # Notification configuration properties
    @property
    def notifications(self) -> Dict[str, Any]:
        """Get the notifications configuration section."""
        return self._config.get("notifications", {})

    @property
    def notifications_enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self.get("notifications.enabled", True)

    @property
    def min_discount_percent(self) -> int:
        """Get the minimum discount percentage to trigger notifications."""
        return self.get("notifications.min_discount_percent", 10)

    @property
    def check_interval_minutes(self) -> int:
        """Get the check interval in minutes."""
        return self.get("notifications.check_interval_minutes", 60)

    # Logging configuration properties
    @property
    def logging(self) -> Dict[str, Any]:
        """Get the logging configuration section."""
        return self._config.get("logging", {})

    @property
    def log_level(self) -> str:
        """Get the logging level."""
        return self.get("logging.level", "INFO")

    @property
    def log_file(self) -> str:
        """Get the log file path."""
        return self.get("logging.file", "sale_notificator.log")


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[Path] = None) -> Config:
    """
    Get the global configuration instance.

    Args:
        config_path: Optional path to config.json. Only used on first call.

    Returns:
        The global Config instance.
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reload_config() -> Config:
    """
    Reload the configuration from disk.

    Returns:
        The reloaded Config instance.
    """
    global _config
    if _config is not None:
        _config.load()
    else:
        _config = Config()
    return _config
