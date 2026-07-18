# Environment Variables

All configuration is environment-based and validated at startup.

| Variable | Purpose |
| --- | --- |
| `APP_ENVIRONMENT`, `APP_DEBUG`, `APP_LOG_LEVEL` | runtime operating mode and observability |
| `DATABASE_URL` | async PostgreSQL connection URL |
| `REDIS_URL` | cache, Celery broker, and result backend URL |
| `BACKEND_CORS_ORIGINS`, `TRUSTED_HOSTS` | browser and host boundary controls |
| `JWT_SECRET_KEY` | HS256 signing secret for access and refresh tokens; rotate through secret management |
| `ACCESS_TOKEN_MINUTES`, `REFRESH_TOKEN_DAYS` | bounded access and refresh-token lifetimes |
| `EMAIL_TOKEN_HOURS`, `PASSWORD_RESET_MINUTES` | one-time token expiry windows |
| `AUTH_RATE_LIMIT_PER_MINUTE` | Redis-backed fixed-window auth endpoint limit per source IP |
| `COOKIE_SECURE` | reserved for a future same-site refresh-cookie delivery mode |
| `S3_*` | reserved object-storage configuration; no uploads are implemented yet |

See `.env.example` for the complete local-development set. Never commit real credentials.
