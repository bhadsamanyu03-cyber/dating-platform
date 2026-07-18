# Authentication

Identity is implemented as a bounded context with opaque one-time email tokens and signed JWTs. `User` stores a normalized email, Argon2 password hash, activity/verification flags, deletion time, and a credential version. Incrementing the credential version invalidates all existing access tokens.

```mermaid
sequenceDiagram
  participant C as Client
  participant A as API
  participant D as PostgreSQL
  participant E as Dev email provider
  C->>A: POST /auth/register
  A->>D: create user + hashed verification token
  A->>E: log verification token
  A-->>C: 201 user
  C->>A: POST /auth/verify-email (opaque token)
  A->>D: consume token and mark email verified
  A-->>C: 204
```

```mermaid
sequenceDiagram
  participant C as Client
  participant A as API
  participant D as PostgreSQL
  C->>A: POST /auth/login
  A->>D: load user, verify Argon2 password
  A->>D: persist hashed refresh session
  A-->>C: access JWT + refresh JWT
```

```mermaid
sequenceDiagram
  participant C as Client
  participant A as API
  participant D as PostgreSQL
  C->>A: POST /auth/refresh
  A->>D: validate session and refresh-token hash
  A->>D: revoke old token; create replacement in same family
  A-->>C: rotated access + refresh JWTs
  Note over A,D: Reuse of revoked token revokes the active family
```

```mermaid
sequenceDiagram
  participant C as Client
  participant A as API
  participant D as PostgreSQL
  participant E as Dev email provider
  C->>A: POST /auth/forgot-password
  A->>D: create hashed one-time reset token
  A->>E: log reset token
  C->>A: POST /auth/reset-password
  A->>D: consume token, update Argon2 hash, revoke sessions
```
