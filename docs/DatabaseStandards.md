# Database Standards

## Confirmed standards

PostgreSQL is the system of record. SQLAlchemy 2 models and Alembic migrations define schema changes. Every schema change must be forward-migratable, reviewable, reversible where practical, indexed for demonstrated access paths, and tested against a PostgreSQL service. Credentials, refresh credentials, and one-time security credentials are never stored in plaintext.

## Open Questions

- What data-retention schedule applies to accounts, audit records, security tokens, and future user content?
- What personal-data deletion, export, and correction workflows are required?
- Which future entities require immutable event history or legal holds?
- What backup retention, restoration testing, and encryption-key policies are required?
