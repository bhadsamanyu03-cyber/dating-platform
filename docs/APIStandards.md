# API Standards

## Confirmed standards

- Public HTTP APIs are versioned under `/api/v1`.
- JSON is the request/response representation for current endpoints.
- Authenticated calls use bearer access tokens; refresh credentials are explicitly supplied to refresh/logout routes.
- Validation and failure responses use the established `{"detail": "..."}` response shape.
- Health and metrics endpoints remain separate operational endpoints.
- New endpoints require OpenAPI documentation, input validation, authorization design, error mapping, tests, and audit implications before implementation.

## Open Questions

- What versioning/deprecation policy and consumer notice period are required?
- Are idempotency keys required for future write endpoints?
- What pagination, filtering, sorting, and field-selection conventions are required?
- Are webhooks, partner APIs, or public API keys in scope?
- What API error codes require stable machine-readable identifiers beyond `detail`?
