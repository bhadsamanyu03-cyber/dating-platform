# Scalability Plan

The current architecture is a deployable modular monolith with independently managed PostgreSQL, Redis, reverse proxy, and worker processes. It should scale through measured bottlenecks, not speculative product design.

## Open Questions

- What launch and growth forecasts require a capacity plan?
- What data sizes, media volumes, and realtime connection counts are expected?
- When is horizontal API/worker scaling, read replication, partitioning, or regional deployment justified?
- What budget, reliability, and operational staffing constraints govern scale decisions?
