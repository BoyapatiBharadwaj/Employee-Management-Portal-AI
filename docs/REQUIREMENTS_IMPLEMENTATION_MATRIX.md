# Requirements Implementation Matrix

This release addresses all previously identified client-gap areas:

| Area | Implementation |
|---|---|
| Superior-role validation | Assignment accepts only employees mapped to Superior/CEO roles; CEO cannot report upward. |
| Historical effective dates | Reporting changes are effective on the configured business date, preserve closed history, reject backwards temporal changes, and prevent cycles. |
| Team evaluation status/performance | Team API joins each direct report to the selected month's evaluation status, scores and rank. |
| Notifications | Persistent notifications have list, unread filter, mark-read and mark-all-read APIs; Admin page and Superior team page consume them. |
| Filters | Admin Insights supports department, Superior, employee, month and rank. |
| Scoped rankings | Overall, department and Superior/team ranking scopes calculate competition rank inside the selected scope. |
| Sorting | Rank, score, employee, department and Superior sorting with ascending/descending order. |
| Attendance/leave inputs | Monthly performance stores the snapshot counts used in normalization, including present/absent/late data and leave request/approval/rejection/unplanned/percentage inputs. |
| Controlled corrections | Finalized evaluations cannot be edited through normal submission; Admin uses a correction endpoint requiring a reason and writing before/after details to AuditLog. |
| Full authorization consistency | Public registration cannot choose a privileged role; users/admin, dashboards, documents, RAG, resume, sentiment, leave, attendance and performance access are restricted server-side. |
| Data integrity | DB indexes/checks plus service-level cycle, temporal, rating, score and unique-month validation. |
| Business timezone | Monthly cycle calculations use `BUSINESS_TIMEZONE` via `ZoneInfo`; audit timestamps remain UTC. |
| Performance/load validation | `scripts/load_test.py` measures p50/p95/p99 and error rate against the 2–3 second target. |
| Scalability | Monthly performance indexes, scoped queries, limited notifications and modular services reduce growth-related hotspots. |
| Availability/infrastructure | Docker restart policies, PostgreSQL healthcheck, backend readiness, frontend healthcheck and dependency ordering are configured. |
| Seven-year retention | Deletion of protected employee HR records is blocked during employment + 7 years; `/retention/status` exposes the calculated protection boundary. |
