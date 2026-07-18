# Testing Requirements

## Confirmed baseline

Backend code is tested with pytest, formatted with Black, and linted with Ruff. CI provisions PostgreSQL and Redis for the authentication integration flow, applies migrations, and executes tests. New behavior requires unit and integration coverage appropriate to its risk.

## Future feature standard

Each feature specification must declare acceptance tests, authorization tests, invalid-input tests, migration tests, reliability tests, observability assertions, and mobile/UI test coverage. Safety-sensitive capabilities require adversarial and abuse-case testing.

## Open Questions

- What overall coverage policy, test ownership, and quality gate is required?
- Which devices, OS versions, locales, network conditions, and accessibility modes require end-to-end testing?
- What load, chaos, security, penetration, and recovery testing is required before launch?
- What test-data privacy and production-data access restrictions apply?
