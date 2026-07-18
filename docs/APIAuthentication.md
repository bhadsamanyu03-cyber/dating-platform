# Authentication API

All routes are prefixed with `/api/v1`. Error responses use FastAPI's consistent `{"detail": "..."}` envelope.

| Endpoint | Auth | Result |
| --- | --- | --- |
| `POST /auth/register` | No | Creates unverified account; sends verification token |
| `POST /auth/login` | No | Access/refresh token pair |
| `POST /auth/logout` | No, refresh token body | Revokes presented refresh session |
| `POST /auth/refresh` | No, refresh token body | Rotates refresh session and returns new pair |
| `POST /auth/verify-email` | No | Consumes verification token |
| `POST /auth/resend-verification` | No | Always accepted to avoid account enumeration |
| `POST /auth/forgot-password` | No | Always accepted to avoid account enumeration |
| `POST /auth/reset-password` | No | Resets password and invalidates sessions |
| `POST /auth/change-password` | Bearer access | Changes password and invalidates sessions |
| `GET /auth/me` | Bearer access | Current identity |
| `GET /auth/sessions` | Bearer access | Active refresh sessions |
| `DELETE /auth/sessions/{id}` | Bearer access | Revokes one owned session |
| `DELETE /auth/account` | Bearer access + password | Soft-deletes the account |
