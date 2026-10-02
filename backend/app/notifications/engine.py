from datetime import datetime, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import (
    Alert,
    AlertNotification,
    NotificationChannel,
    NotificationGroupMember,
    NotificationPolicy,
    NotificationPolicyChannel,
    NotificationRecipient,
    NotificationTemplate,
)


def enqueue_alert_notifications(alert_id: int) -> int:
    now = datetime.now(timezone.utc)
    created = 0
    with SessionLocal() as db:
        alert = db.get(Alert, alert_id)
        if alert is None:
            return 0

        policies = db.scalars(
            select(NotificationPolicy).where(
                NotificationPolicy.enabled.is_(True),
                NotificationPolicy.event_type == "ALERT_TRIGGERED",
                (NotificationPolicy.severity.is_(None) | (NotificationPolicy.severity == alert.severity)),
            )
        ).all()

        for policy in policies:
            channels = db.scalars(
                select(NotificationChannel)
                .join(NotificationPolicyChannel, NotificationPolicyChannel.channel_id == NotificationChannel.id)
                .where(
                    NotificationPolicyChannel.policy_id == policy.id,
                    NotificationChannel.enabled.is_(True),
                )
            ).all()

            for channel in channels:
                recipients = db.scalars(
                    select(NotificationRecipient)
                    .join(NotificationGroupMember, NotificationGroupMember.recipient_id == NotificationRecipient.id)
                    .where(
                        NotificationGroupMember.group_id.in_(
                            select(NotificationPolicyChannel.policy_id).where(NotificationPolicyChannel.policy_id == policy.id)
                        ),
                        NotificationRecipient.enabled.is_(True),
                    )
                ).all()
                # Recipient groups are resolved by policy configuration in the next iteration.
                # Keep channel/policy records enqueueable even when no recipient group exists.
                if not recipients:
                    db.add(AlertNotification(
                        alert_id=alert.id,
                        policy_id=policy.id,
                        channel_id=channel.id,
                        recipient_id=None,
                        status="PENDING",
                        created_at=now,
                    ))
                    created += 1
        db.commit()
    return created
