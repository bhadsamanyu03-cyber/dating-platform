# Error Handling

## Confirmed standards

Current API validation and domain failures return a consistent JSON `detail` field with appropriate HTTP status codes. Authentication endpoints avoid revealing whether an account exists for resend-verification and password-reset requests. Unexpected server failures must not disclose internals.

## Future feature standard

Every feature must define user-facing recovery language, stable API error behavior, retry safety, observability events, support escalation, and handling for offline/timeout/replay states before implementation.

## Open Questions

- Which domain error identifiers must remain stable for client behavior?
- What retry, backoff, and idempotency guidance applies by operation?
- What support contact, diagnostics, and status-page behavior is required?
- Which failures require user notification or administrator escalation?
