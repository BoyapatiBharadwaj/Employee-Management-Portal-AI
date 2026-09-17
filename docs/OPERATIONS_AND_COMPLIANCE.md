# Operations & Compliance Notes

## Business timezone
All monthly hierarchy/performance boundaries use `BUSINESS_TIMEZONE` (default `Asia/Kolkata`) through the backend business-date helper. UTC remains the storage timezone for audit timestamps.

## Availability design
Docker Compose uses `restart: unless-stopped`, PostgreSQL readiness checks, backend readiness checks, and frontend health checks. The backend exposes `/health/live` and `/health/ready`. A hosted 99% business-availability target additionally requires a production platform with monitoring, backups, TLS, persistent volumes, and an appropriate deployment topology; the application cannot guarantee infrastructure uptime by itself.

## Performance validation
Run `python scripts/load_test.py --base-url http://localhost:8000 --path /health/ready` and then run an authenticated endpoint such as `/performance/insights` after seeding data. The script reports p50/p95/p99 latency and error rate and treats <=3s p95 with 0% HTTP errors as a pass for the client target.

## Data retention
The application protects employee deletion, historical performance deletion, user deletion linked to protected employees, and offboarding deletion while HR records are inside the configured employment + 7-year retention window. A terminated employee's last working day is obtained from Offboarding; active employees remain protected. `GET /retention/status` exposes the calculated retention boundary for authorized users.

## Controlled performance corrections
Finalized monthly performance records are immutable through the normal evaluation API. HR/Admin corrections must use `/performance/monthly/correct`, provide a reason, and create an audit entry with the before/after values.

## Security boundary
Public registration always creates an Employee account. Privileged role assignment is restricted to Admin-managed user updates. Sensitive organization-wide endpoints use server-side role checks; hierarchy/performance visibility is additionally constrained by the reporting relationship.
