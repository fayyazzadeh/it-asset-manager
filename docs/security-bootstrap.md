# Security bootstrap and deployment

## Production configuration

Set these values through the deployment environment or secret manager; do not commit them to Git:

- `ENVIRONMENT=production`
- `JWT_SECRET`: at least 32 characters of high-entropy random data.
- `POSTGRES_PASSWORD`: a unique, strong database password. If it contains URL-reserved characters, URL-encode it when supplying `DATABASE_URL` directly.
- `BOOTSTRAP_ADMIN_ENABLED=false` after the first administrator is created.

The API validates production JWT and database credentials during settings initialization and refuses known development defaults. Keep `ENVIRONMENT=development` only for local development.

## Create the first administrator

Registration is disabled unless `BOOTSTRAP_ADMIN_ENABLED=true`. The flag only permits creation while the `users` table is empty. The API takes a PostgreSQL table lock and re-checks the table before assigning the ADMIN role, preventing concurrent bootstrap requests from both becoming administrators.

1. Configure the production database and a strong `JWT_SECRET`.
2. Temporarily set `BOOTSTRAP_ADMIN_ENABLED=true` in the API service environment.
3. Start/restart the API and send one registration request to `POST /api/auth/register` with a unique username, email, and strong password. This one-time bootstrap endpoint is not authenticated; its explicit environment flag and empty-database check gate access. The endpoint returns access and refresh tokens; store them securely.
4. Immediately set `BOOTSTRAP_ADMIN_ENABLED=false` and restart the API service.
5. Verify a second registration is rejected, then verify the new administrator can log in and access `GET /api/auth/me`.

If the users table already contains any account, the bootstrap endpoint refuses to create another account, even if the flag remains enabled. Normal user provisioning should be implemented as an administrator-only workflow before multi-user rollout; public self-registration is intentionally not supported by this change.

## Authorization policy

- `GET /api/assets` and `GET /api/assets/{asset_id}`: ADMIN, OPERATOR, VIEWER, AUDITOR.
- `POST /api/assets`: ADMIN, OPERATOR.
- `POST /api/discovery/preview`: ADMIN, OPERATOR.
- `GET /api/auth/me`: any active user with at least one role.
- `/health`, login and refresh remain public; registration is guarded by the one-time bootstrap policy.

Role assignments are loaded from PostgreSQL on each authenticated request so role revocations are effective without waiting for an access token to expire. API clients must send `Authorization: Bearer <access_token>`.

## Deployment caution

This branch intentionally changes API behavior: existing clients that call asset or discovery endpoints without a bearer token will receive HTTP 401, and authenticated users without a permitted role will receive HTTP 403. Update clients and perform integration testing before merging. These changes have not been deployed to production.
