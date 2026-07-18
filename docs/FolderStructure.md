# Folder Structure

- `apps/` — deployable clients and services.
- `apps/mobile/` — Expo TypeScript mobile boundary.
- `apps/backend/` — FastAPI service, migration tooling, and tests.
- `packages/` — framework-neutral TypeScript packages.
- `packages/shared-types/` — cross-client contracts.
- `packages/shared-utils/` — pure reusable client utilities.
- `infrastructure/` — operational configuration.
- `infrastructure/docker/` — Docker-oriented assets.
- `infrastructure/nginx/` — reverse-proxy policy.
- `infrastructure/github/` — explanation of GitHub-specific configuration.
- `.github/workflows/` — GitHub-required CI workflow location.
- `docs/` — engineering documentation.
- `scripts/` — developer and operational automation.
