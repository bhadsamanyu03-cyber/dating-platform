# AI Engineering Rules

## Purpose and precedence

These rules govern all future engineering work in this repository. Follow them together with the frozen PRD, the current engineering backlog, repository documentation, and explicit product-owner instructions. Where sources conflict: explicit product-owner instruction and a newer approved PRD decision win; otherwise preserve the frozen PRD and ask for clarification rather than inventing behavior.

## Required pre-work

1. Read `docs/EngineeringBacklog.md`, relevant product/security/API/database documents, and the affected existing code before changing anything.
2. State the milestone, dependency status, scope, non-goals, and acceptance criteria being addressed.
3. Do not start a milestone whose listed prerequisites are incomplete or unverified.
4. If a needed product decision is not frozen, stop and add/request an explicit decision; do not infer it from common dating-app patterns.

## Scope protection

- Implement only approved backlog scope. Preserve every explicit exclusion.
- Never add product capabilities, fields, API routes, analytics, third-party dependencies, or UX behavior because they seem conventional.
- Treat moderation providers as optional integrations; the application must function without one.
- Do not introduce a web client, payments, premium features, location tracking, AI matchmaking, stories, livestreaming, voice/video calls, or other PRD exclusions.

## Engineering quality

- Produce production-quality implementations: no TODOs, placeholder architecture, dummy services, mocked production paths, fake APIs, or silently failing behavior.
- Follow SOLID, clean boundaries, dependency injection, explicit resource lifecycle, and configuration through environment variables.
- Keep the FastAPI modular monolith, React Native/Expo client, PostgreSQL, Redis, Celery, S3-compatible storage, Docker/Nginx, and CI foundation unless an approved architecture decision changes it.
- Do not use global mutable application state. Keep domain logic out of route handlers and infrastructure adapters.
- Make external integrations replaceable behind interfaces and test their failure modes.

## Data and API changes

- Model domain invariants explicitly. Add a reviewed Alembic migration for every persistent schema change; include indexes, constraints, forward migration, and safe rollback reasoning.
- Never store plaintext passwords, refresh credentials, reset credentials, or secrets. Minimize personal-data collection and document retention/deletion impact.
- Version public APIs under the established API prefix. Define validation, authorization, status codes, stable error behavior, idempotency/concurrency behavior, OpenAPI documentation, and audit effects before implementation.
- Enforce authorization server-side on every resource and every realtime operation; client checks are never sufficient.

## Security and safety

- Preserve Argon2, JWT expiry/type validation, refresh rotation/replay handling, rate limits, HTTPS expectations, trusted-host validation, security headers, structured request logs, audit logs, and session controls.
- Threat-model every new feature for authorization bypass, abuse, privacy leakage, enumeration, replay, injection, unsafe uploads, and denial of service.
- For social features, define block/report/suspension/content-removal behavior across all affected surfaces before implementation.
- Never log secrets, access/refresh tokens, reset/verification tokens, passwords, or sensitive user content.

## Testing and verification

- Add unit tests, PostgreSQL/Redis-backed integration tests where applicable, negative authorization tests, invalid-input tests, concurrency/idempotency tests, and migration tests for each feature.
- Add mobile/UI, accessibility, realtime, media, performance, security, and failure-mode tests when the feature touches those concerns.
- Run and report the configured formatter, linter, tests, build, and relevant migration checks. Do not claim checks passed if the environment prevented them; state the exact limitation.
- Update CI when a feature adds a dependency, runtime service, migration, or test environment need.

## Documentation and completion

- Update architecture, API, security, environment, development, and feature documentation whenever behavior changes.
- Include acceptance criteria, observability, error handling, operations, and release/rollback impact in the handoff.
- A feature is complete only when it meets `docs/DefinitionOfDone.md`, its backlog acceptance criteria, and the frozen PRD. Compilation alone is not completion.
- Before proposing the next milestone, confirm all dependencies, acceptance criteria, tests, docs, and open product decisions are resolved.
