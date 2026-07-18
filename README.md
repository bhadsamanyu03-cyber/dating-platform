# Dating Platform Monorepo — Phase 1

Production-oriented infrastructure foundation for a React Native / FastAPI dating platform. This phase deliberately contains no authentication, profiles, media, or dating-domain logic.

## Start locally

```sh
cp .env.example .env
docker compose up --build
```

Then visit `http://localhost:8080/health/live` and `http://localhost:8080/docs`.

See [DevelopmentGuide](docs/DevelopmentGuide.md) for details.
