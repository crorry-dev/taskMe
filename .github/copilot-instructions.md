# Copilot Instructions (Load First)

## 🚨 ABSOLUTE PRIORITY RULE (Always Highest)
**Self-Improvement Mandate**: If you recognize that these instructions, project structure, agent configurations, or any aspect of the development workflow could be improved, **immediately suggest and implement the improvement**. This includes:
- Restructuring these instructions for clarity
- Adding missing patterns or conventions
- Proposing better tooling, automation, or AI agent configurations
- Identifying architectural anti-patterns
- Suggesting performance, security, or UX improvements

The goal is **absolute perfection** - code that world-class developers would find flawless.

---

## 0) Purpose
You are contributing to **CommitQuest**, a security-first commitment ToDo + Challenge platform. Always align changes with: highest security standard, React + Django stack, Apple-like UI/UX, and smooth collaboration across devices/developers/models.

---

## 0.1) Project Context (Quick Reference)
```
Backend:  Django 4.2 + DRF | Python 3.9+ | venv: .venv/
Frontend: React 19 + MUI 5 | Node 18+
Database: SQLite (dev) / PostgreSQL (prod)
AI:       OpenAI API (Whisper + GPT-4o-mini)
```

**Key Directories:**
- `backend/` - Django project with apps: accounts, challenges, rewards, teams, tasks, notifications, debug_feedback
- `frontend/src/` - React app with pages/, components/, services/, contexts/
- `.github/` - CI/CD, copilot instructions

---

## 0.2) Special Users & Permissions
| Username | Role | Special Powers |
|----------|------|----------------|
| `crorry` | Admin | Unlimited credits, full debug access, no restrictions |

---

## 1) Non-negotiable Requirements (Always)
### 1.1 Security: "Unhackable" target
Treat this as **high assurance** software.
- Follow OWASP Top 10 + ASVS mindset.
- Never trust client input. Validate on server.
- Enforce authorization on every request (object-level checks).
- Use least privilege everywhere (RBAC/ABAC).
- Add rate limiting & abuse protection on auth + write endpoints.
- Sanitize/validate file uploads; restrict types/sizes; store safely.
- Secrets never in repo; use env; do not log secrets/PII.
- Prefer secure defaults: private visibility, minimal data collection.
- Add/extend audit logs for sensitive operations.

### 1.2 Tech Stack
- Frontend: **React + TypeScript** (modern patterns).
- Backend: **Django** + REST API (DRF or Django Ninja).
- DB: PostgreSQL; cache/queue via Redis/Celery when needed.
- Use modern tooling: Docker/Compose, linting, formatting, CI.

### 1.3 UI/UX (Apple-like)
- Minimalistic, consistent spacing, strong typography hierarchy.
- Intuitive flows; reduce configuration on primary paths.
- Accessibility: keyboard support, focus states, aria labels, contrast, reduced motion.

---

## 2) Product Scope Anchors
Core objects:
- Challenge types: Todo, Streak, Program, Quantified, Team aggregated, Duel, Team vs Team, Community/Global events (later).
- Proof types: SELF, PHOTO, VIDEO (later), DOCUMENT, PEER, SENSOR (later).
- Rewards: XP/Level, Streaks, Badges.

MVP focus:
- SELF + PHOTO + PEER proof
- Solo + Team + Duel
- Basic leaderboard + notifications

Avoid implementing: payments, gambling-like stakes, broad public leaderboards at country scale in MVP.

---

## 3) Coding Standards
### 3.1 General
- Prefer small, reviewable diffs.
- Write tests alongside features.
- Keep naming consistent; avoid cleverness.

### 3.2 Frontend (React/TS)
- Strict TypeScript, no `any` unless justified.
- Use typed API clients; never hardcode URLs without config.
- Validate forms client-side, but assume server is authoritative.
- Use components that encourage consistency (design system approach).
- Accessibility required: aria, focus, keyboard nav.

### 3.3 Backend (Django)
- Use explicit serializers/schemas; validate input.
- Enforce object-level permissions (e.g., user can only modify own items).
- Use transactions for multi-step writes.
- Add audit log entries for: auth events, membership changes, proof approval, challenge visibility changes.
- Avoid N+1 queries; use select_related/prefetch_related.

---

## 4) Security Checklist for Every PR
- [ ] AuthN: secure sessions/JWT handling, CSRF where applicable
- [ ] AuthZ: object-level permission checks
- [ ] Input validation & output encoding
- [ ] Rate limiting / abuse controls on sensitive endpoints
- [ ] File upload restrictions (type, size, storage isolation)
- [ ] Logging: no secrets; minimal PII; include request IDs
- [ ] Tests for permissions and negative cases

If any item is not applicable, document why in code comments or PR notes.

---

## 5) Repo & Collaboration Conventions
- Keep environment reproducible: update Docker/Compose when dependencies change.
- Document architectural decisions with ADRs in `docs/ADR/`.
- Update API contracts (OpenAPI) whenever endpoints change.
- Maintain consistent formatting:
  - Frontend: prettier + eslint
  - Backend: ruff/black + isort (choose and standardize)
- Use conventional commits (optional) but consistent messaging.

---

## 6) Preferred Implementation Patterns
- API-first: React consumes typed API; avoid server-rendered coupling.
- Typed shared contracts: consider `openapi` + generated clients or shared zod schemas.
- Use feature flags for risky/unfinished features.
- Prefer "private by default" visibility and explicit sharing.

---

## 7) Debug Feedback System (QA/Testing Mode)
The project includes an AI-powered debug feedback system for testers and developers.

### 7.1 How It Works
1. **Input**: Testers submit feedback via voice memo or text (e.g., "Das Blau gefällt mir nicht")
2. **Transcription**: Voice memos are transcribed via OpenAI Whisper
3. **AI Analysis**: GPT-4o-mini analyzes feedback and suggests code changes
4. **Implementation**: Changes can be auto-implemented (with approval)
5. **Version Control**: Each change is committed automatically

### 7.2 Key Files
- `backend/debug_feedback/` - Django app with models, views, services
- `frontend/src/components/debug/DebugPanel.js` - Floating UI component
- `frontend/src/services/debugService.js` - API client

### 7.3 Credit System
- Each feedback analysis costs 1 credit
- Users in `DebugConfig.unlimited_credit_usernames` bypass costs
- Default unlimited users: `['crorry']`

### 7.4 Safety Rules
- Only files in `frontend/src/` and `backend/` can be modified
- Sensitive files blocked: settings.py, migrations, .env, manage.py
- Admin approval required by default (configurable)

---

## 8) What to do when unclear
If requirements conflict, prioritize in order:
1) Security & privacy
2) Correctness & tests
3) UX consistency
4) Performance
5) Convenience

Make reasonable assumptions, document them in code comments and/or ADR.
