# Architecture

Consolidated Architecture v2 is the source of truth.

Principles:
- Asset identity is independent of IP address.
- Discovery is separate from monitoring.
- Lifecycle status is separate from monitoring state.
- Events are separate from alerts.
- Alerts are separate from notifications.
- Audit logs are separate from change history.
- Long-running work runs in Celery workers.
- Connectors produce observations before asset state is mutated.