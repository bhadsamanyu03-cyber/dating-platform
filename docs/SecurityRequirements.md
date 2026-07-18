# Security Requirements

## Confirmed controls

Identity controls are specified in [Security](Security.md). They include Argon2 password hashing, token expiration, refresh rotation and replay containment, credential-version invalidation, hashed one-time tokens, trusted-host checks, CORS configuration, security headers, rate-limit hooks, request logging, and audit records.

Every future feature must define authorization, abuse prevention, privacy impact, audit events, threat model, and test cases before implementation.

## Open Questions

- What age assurance, identity verification, or jurisdiction-specific controls are required?
- What moderation, reporting, blocking, and anti-harassment safety policies apply?
- Which roles may access administrative data and which approvals are required?
- What incident-response, breach-notification, and vulnerability-remediation commitments apply?
- What legal basis, consent, and privacy-request processes apply to personal data?
