# Coding Standards

Backend code targets Python 3.13, uses type annotations, follows Clean Architecture boundaries, and is formatted with Black and linted with Ruff. Infrastructure code is explicit and environment-driven. Tests use pytest and must cover behavior rather than implementation details.

Mobile and packages use TypeScript strict mode, ESLint, Prettier, and Jest. Domain logic must not be placed in transport handlers, global state, or framework-specific shared packages.
