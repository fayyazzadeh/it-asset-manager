from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    subject_template: Mapped[str] = mapped_column(String(300), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(50))
    webhook_url: Mapped[str | None] = mapped_column(String(1000))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NotificationGroup(Base):
    __tablename__ = "notification_groups"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class NotificationGroupMember(Base):
    __tablename__ = "notification_group_members"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("notification_groups.id", ondelete="CASCADE"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("notification_recipients.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (UniqueConstraint("group_id", "recipient_id"),)


class NotificationChannel(Base):
    __tablename__ = "notification_channels"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    channel_type: Mapped[str] = mapped_column(String(30), nullable=False)
    configuration: Mapped[dict | None] = mapped_column(JSONB)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NotificationPolicy(Base):
    __tablename__ = "notification_policies"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str | None] = mapped_column(String(30))
    template_id: Mapped[int] = mapped_column(ForeignKey("notification_templates.id", ondelete="RESTRICT"), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NotificationPolicyChannel(Base):
    __tablename__ = "notification_policy_channels"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("notification_policies.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("notification_channels.id", ondelete="RESTRICT"), nullable=False)
    __table_args__ = (UniqueConstraint("policy_id", "channel_id"),)


class AlertNotification(Base):
    __tablename__ = "alert_notifications"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    policy_id: Mapped[int] = mapped_column(ForeignKey("notification_policies.id", ondelete="RESTRICT"), nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("notification_channels.id", ondelete="RESTRICT"), nullable=False)
    recipient_id: Mapped[int | None] = mapped_column(ForeignKey("notification_recipients.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (
        Index("ix_alert_notifications_alert_status", "alert_id", "status"),
        Index("ix_alert_notifications_status_created", "status", "created_at"),
    )
