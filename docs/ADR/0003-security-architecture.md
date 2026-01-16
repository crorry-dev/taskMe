# ADR 0003: Security Architecture

## Status
Accepted

## Context
As a commitment-based application handling user data, proofs (including photos/videos), and social features, security is critical.

## Decision

### Authentication
- JWT with short-lived access tokens (60 min default)
- Refresh token rotation with blacklisting
- Rate limiting on auth endpoints (10/min for login, 3/hour for password reset)
- MFA-ready architecture (TOTP in Phase 2)

### Authorization
- Object-level permissions on all resources
- RBAC for team roles (owner, admin, member)
- Challenge visibility levels (private, team-only, public)
- Proof review permissions based on challenge settings

### Input Validation
- Server-side validation for all inputs (never trust client)
- Django serializer validation + custom validators
- File upload: allowlist extensions, server-side MIME check, size limits
- SQL injection protection via ORM (parameterized queries)

### Security Headers
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
```

### Audit Logging
All security-relevant events logged with:
- Request ID
- User ID (if authenticated)
- IP address (hashed for privacy)
- Action type
- Resource affected
- Timestamp

### Secrets Management
- Never in code or version control
- Environment variables (python-decouple)
- Production: secrets manager integration ready

## Rationale
- Defense in depth approach
- OWASP Top 10 coverage
- Audit trail for compliance and incident response

## Consequences
- Slightly more complex implementation
- Performance overhead from logging (acceptable)
- Need for log aggregation solution in production
