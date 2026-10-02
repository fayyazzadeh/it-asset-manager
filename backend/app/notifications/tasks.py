from datetime import datetime, timezone
from email.message import EmailMessage
import smtplib

from sqlalchemy import select

from app.core.config import settings
from app.db import SessionLocal
from app.models import AlertNotification, NotificationChannel, NotificationPolicy, NotificationRecipient, NotificationTemplate
from app.workers.celery_app import celery_app


def _render(template: str, values: dict[str, object]) -> str:
    return template.format_map({key: str(value) for key, value in values.items()})


def _send_email(recipient: str, subject: str, body: str) -> None:
    if not settings.smtp_host or not settings.smtp_from:
        raise RuntimeError("SMTP notification settings are not configured")

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)


@celery_app.task(name="notifications.deliver_pending")
def deliver_pending_notifications(limit: int = 100) -> int:
    processed = 0
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        rows = db.execute(
            select(AlertNotification, NotificationChannel, NotificationRecipient, NotificationTemplate)
            .join(NotificationChannel, NotificationChannel.id == AlertNotification.channel_id)
            .outerjoin(NotificationRecipient, NotificationRecipient.id == AlertNotification.recipient_id)
            .join(NotificationPolicy, NotificationPolicy.id == AlertNotification.policy_id)
            .join(NotificationTemplate, NotificationTemplate.id == NotificationPolicy.template_id)
            .where(AlertNotification.status == "PENDING")
            .order_by(AlertNotification.created_at)
            .limit(limit)
        ).all()

        for notification, channel, recipient, template in rows:
            notification.attempts += 1
            try:
                if channel.channel_type != "EMAIL":
                    raise RuntimeError(f"unsupported notification channel: {channel.channel_type}")
                if recipient is None or not recipient.email:
                    raise RuntimeError("notification recipient has no email address")

                subject = _render(template.subject_template, {"alert_id": notification.alert_id})
                body = _render(template.body_template, {"alert_id": notification.alert_id})
                _send_email(recipient.email, subject, body)
                notification.status = "SENT"
                notification.sent_at = now
            except Exception as exc:
                notification.status = "FAILED"
                notification.last_error = str(exc)
            processed += 1

        db.commit()

    return processed
