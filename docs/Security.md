# Security

- Passwords are restricted to 12–128 characters, require mixed case and digits, reject a baseline weak-password list, and are hashed with Argon2.
- Access JWTs are HS256 signed, short lived, type-bound, and carry a credential version. Refresh JWTs are type-bound and session-bound.
- Refresh tokens are stored only as SHA-256 hashes. Rotation revokes the presented session and creates a replacement in the same family; use of a revoked member revokes that family.
- Email verification and password-reset credentials are high-entropy opaque tokens stored only as hashes, expire, and are single-use.
- Password change/reset and account deletion increment credential version and revoke every active refresh session. Account deletion is a soft deletion.
- Trusted hosts, explicit CORS origins, standard security headers, structured request logging, audit logging, and Redis-backed auth-rate-limit hooks are enabled.

## CSRF and token delivery

The mobile API returns bearer tokens in JSON and clients must keep refresh tokens in platform secure storage (iOS Keychain / Android Keystore), not web storage. Bearer headers are not automatically attached by browsers and therefore do not require cookie CSRF defenses. If a browser refresh-cookie mode is later enabled, it must use `Secure`, `HttpOnly`, `SameSite` settings appropriate to the frontend topology plus a CSRF token/origin validation strategy. `COOKIE_SECURE` exists for that deployment mode but no cookie is currently emitted.
