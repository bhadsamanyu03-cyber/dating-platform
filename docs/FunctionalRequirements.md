# Functional Requirements

## Confirmed identity requirements

- A person can register with an email address and password.
- A person can log in, obtain access and refresh credentials, rotate a refresh credential, log out, and view/revoke active sessions.
- A person can verify an email address, request a password-reset credential, reset a password, change a password, view the current account, and soft-delete an account.
- Authentication failures and relevant account events are recorded for audit purposes.

## Unspecified functional areas

There are no approved requirements for profiles, discovery, matching, messaging, media, moderation, notifications, billing, administrative operations, analytics, or customer support tooling. No behavior in these areas may be implemented from this document.

## Open Questions

- Is verified email required before use of future product functionality?
- Is sign-in by any method other than email and password required?
- Is account recovery required when email access is lost?
- What is the required behavior after a soft-deleted account is restored or expires?
- Which future features require an identity or age-verification gate?
