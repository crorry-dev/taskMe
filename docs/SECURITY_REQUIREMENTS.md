# Security Requirements (Authoritative)

These requirements are mandatory for all features.

## A) Principles
- Zero trust: all inputs untrusted.
- Least privilege: minimize access per role/action.
- Secure defaults: private visibility, minimal data retention.
- Defense in depth: validation + authz + rate limiting + auditing.

## B) Web/API Controls
- Strong authentication strategy (MFA-ready).
- CSRF protection if cookie-based auth is used.
- Rate limiting on auth and write endpoints.
- Strict CORS policy; no wildcard in production.
- Content Security Policy (CSP) on web app.
- Secure headers: HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy.

## C) Authorization
- Object-level authorization required for all reads/writes.
- Team membership and roles must gate access.
- Proof review actions restricted to permitted reviewers.

## D) File Uploads (Proof)
- Allowlist types; enforce size limits.
- Store files in isolated bucket/path per tenant/user.
- Use signed URLs; never expose raw storage credentials.
- Perform server-side validation; do not trust MIME from client.
- Optional later: malware scanning pipeline.

## E) Data Protection
- TLS everywhere.
- Encryption at rest (DB + storage, infra-dependent).
- PII minimization; redact in logs.
- User data export/delete flows planned.

## F) Auditability
- Audit logs for sensitive actions:
  - login/logout, password reset, MFA changes
  - membership/role changes
  - challenge visibility/rules changes
  - proof submissions and approvals/rejections
- Logs must be structured and include request IDs.

## G) Dependency & Supply Chain
- Lockfiles committed.
- CI: SCA, lint, tests.
- No secrets in repo; secret scanning enabled.
