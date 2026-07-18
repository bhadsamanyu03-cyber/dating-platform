# Deployment Targets

The current local stack uses Docker Compose for backend, PostgreSQL, Redis, Nginx, and a worker. CI runs lint, formatting checks, migrations, and tests. No production hosting target has been selected.

## Open Questions

- Which cloud, regions, accounts, environments, and network boundaries are approved?
- What domain, TLS, DNS, secrets, certificate, and identity-management strategy is required?
- What deployment approvals, rollback procedures, maintenance windows, and disaster-recovery requirements apply?
- What monitoring, logging, tracing, backup, and incident-management providers are approved?
