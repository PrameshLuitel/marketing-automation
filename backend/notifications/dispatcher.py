"""
Notification dispatch — Email (SMTP), Slack webhook, Telegram bot.
All channels are free.
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger

try:
    import requests
except ImportError:
    requests = None


class NotificationDispatcher:
    """Sends notifications via Email, Slack, and Telegram."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "")
        self.email_to = os.getenv("NOTIFICATION_EMAIL_TO", "")

        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    async def send_all(self, subject: str, message: str, data: Optional[dict] = None):
        """Send notification to all configured channels."""
        results = {}

        if self.smtp_user and self.email_to:
            results["email"] = self._send_email(subject, message)
        if self.slack_webhook:
            results["slack"] = self._send_slack(subject, message)
        if self.telegram_token and self.telegram_chat_id:
            results["telegram"] = self._send_telegram(subject, message)

        if not results:
            logger.warning("No notification channels configured")

        return results

    def _send_email(self, subject: str, body: str) -> bool:
        """Send notification via SMTP email."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🚀 Marketing AI: {subject}"
            msg["From"] = self.smtp_from
            msg["To"] = self.email_to

            # HTML email
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #6c63ff; margin-top: 0;">📊 {subject}</h2>
                    <div style="color: #333; line-height: 1.6;">
                        {body.replace(chr(10), '<br>')}
                    </div>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px;">
                        Sent by Marketing Department Automation AI
                    </p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.success(f"Email sent to {self.email_to}")
            return True

        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    def _send_slack(self, subject: str, message: str) -> bool:
        """Send notification via Slack webhook."""
        if not requests:
            return False

        try:
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": f"📊 {subject}"},
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": message[:2900]},
                    },
                    {"type": "divider"},
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "🤖 _Marketing Department Automation AI_",
                            }
                        ],
                    },
                ]
            }

            resp = requests.post(
                self.slack_webhook,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if resp.status_code == 200:
                logger.success("Slack notification sent")
                return True
            else:
                logger.error(f"Slack webhook returned {resp.status_code}")
                return False

        except Exception as e:
            logger.error(f"Slack send failed: {e}")
            return False

    def _send_telegram(self, subject: str, message: str) -> bool:
        """Send notification via Telegram bot."""
        if not requests:
            return False

        try:
            text = f"📊 *{subject}*\n\n{message[:3500]}"
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"

            resp = requests.post(
                url,
                json={
                    "chat_id": self.telegram_chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
                timeout=10,
            )

            if resp.status_code == 200:
                logger.success("Telegram notification sent")
                return True
            else:
                logger.error(f"Telegram API returned {resp.status_code}")
                return False

        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False

    async def send_campaign_summary(self, campaign_data: dict):
        """Send a formatted campaign summary notification."""
        quality = campaign_data.get("quality_score", 0)
        passed = campaign_data.get("passed_quality_gate", False)
        run_id = campaign_data.get("run_id", "unknown")

        subject = f"Campaign Generated — Score: {quality}/10 {'✅' if passed else '⚠️'}"
        message = f"""**Run ID:** {run_id}
**Quality Score:** {quality}/10
**Status:** {'Passed Quality Gate ✅' if passed else 'Needs Review ⚠️'}
**Duration:** {campaign_data.get('duration_seconds', 0)}s

**Agents Used:**
"""
        for log in campaign_data.get("logs", []):
            message += f"• {log['agent']} → {log['provider']} ({log['tokens']} tokens)\n"

        message += f"\nReview the campaign in the dashboard."

        return await self.send_all(subject, message)
