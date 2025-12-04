import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List


class EmailNotifier:
    """Sends email notifications for price alerts."""

    def __init__(self, config: Dict):
        self.smtp_server = config['smtp_server']
        self.smtp_port = config['smtp_port']
        self.sender_email = config['sender_email']
        self.sender_password = config['sender_password']
        self.recipient_email = config['recipient_email']
        self.use_tls = config.get('use_tls', True)

    def send_alert(self, item_name: str, url: str, current_price: float,
                   threshold: float, currency: str) -> bool:
        """Send a price alert email for a single item."""
        subject = f"Price Alert: {item_name}"

        body = f"""
Price Alert!

The price for "{item_name}" has dropped below your threshold.

Current Price: {current_price:,.2f} {currency}
Your Threshold: {threshold:,.2f} {currency}
Savings: {threshold - current_price:,.2f} {currency}

Product Link: {url}

---
This is an automated message from SaleNotificator.
        """.strip()

        return self._send_email(subject, body)

    def send_batch_alert(self, alerts: List[Dict]) -> bool:
        """Send a single email with multiple price alerts."""
        if not alerts:
            return True

        subject = f"Price Alert: {len(alerts)} item(s) below threshold"

        body_parts = ["Price Alert!\n\nThe following items have dropped below your threshold:\n"]

        for i, alert in enumerate(alerts, 1):
            body_parts.append(f"""
{i}. {alert['name']}
   Current Price: {alert['current_price']:,.2f} {alert['currency']}
   Your Threshold: {alert['threshold']:,.2f} {alert['currency']}
   Savings: {alert['threshold'] - alert['current_price']:,.2f} {alert['currency']}
   Link: {alert['url']}
""")

        body_parts.append("\n---\nThis is an automated message from SaleNotificator.")

        return self._send_email(subject, '\n'.join(body_parts))

    def _send_email(self, subject: str, body: str) -> bool:
        """Send an email with the given subject and body."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            return True

        except Exception as e:
            raise NotifierError(f"Failed to send email: {e}")


class NotifierError(Exception):
    """Exception raised when notification fails."""
    pass
