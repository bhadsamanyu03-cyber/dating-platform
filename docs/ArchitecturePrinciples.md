# Architecture Principles

1. Preserve the modular-monolith architecture until a measured need and explicit decision justify change.
2. Keep bounded contexts explicit; do not leak product-domain logic into transport, infrastructure, or shared utility layers.
3. Use dependency injection, environment-based configuration, structured logging, and managed resource lifecycles.
4. Treat PostgreSQL as the system of record and manage schema evolution through reviewed Alembic migrations.
5. Make security, privacy, observability, failure behavior, and testing first-class feature requirements.
6. Prefer documented product-owner decisions over assumed product conventions.
7. Build no feature that has not been specified and accepted.
