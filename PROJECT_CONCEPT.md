# CommitQuest (Arbeitstitel) – Projektkonzept

## 1. Vision
CommitQuest verwandelt Aufgaben in echte Commitments: Nutzer erstellen To-dos, Streaks, Programme, Team- und Community-Challenges. Der Ersteller kann Beweispflichten definieren (z. B. Foto/Video/Dokument/Peer-Verifikation/Sensor-Import). Motivation entsteht durch Belohnungen, Progression, soziale Dynamik (Duels/Teams) und globale Events (z. B. NoShave November).

## 2. Kernprobleme, die gelöst werden
- Prokrastination bei Alltagstasks („Wäsche machen").
- Durchhalteprobleme bei Gewohnheitsbruch („kein Alkohol", „keine Zigarette").
- Zielverfolgung bei längeren Programmen („30 Tage 10 km täglich").
- Team-Commitments und Wettbewerb („10.000 Push-ups als Team").
- Kollektiver Impact („Deutschland/Hessen/Stadt/Verein/Familie/Paar spendet Summe X").
- Direkte Provokations-Challenges („Nutzer XY, das schaffst du nie").

## 3. Produktprinzipien
1) Commitment statt Checkbox: Jede Aufgabe hat Regeln, Zeitrahmen und (optional) Proof.
2) Skalierbare Strenge: Proof-Level von „Selbstbestätigung" bis „Sensor-Daten".
3) Positive Motivation: Rewards, Streaks, Badges, Reputation; keine toxische Beschämung.
4) Social by Design: Duels, Teams, Feed, Leaderboards – aber privacy-first.
5) Security-first: Highest standard, hardening, auditability, least privilege, secure defaults.
6) Cross-device & multi-dev: Reproduzierbare Builds, klare Konventionen, starke Dokumentation.

## 4. Zielgruppen
- Einzelpersonen (Habits, Alltag, Sport).
- Freunde/Paare/Familien (gemeinsame Ziele).
- Vereine/Teams/Firmen (Team-Challenges).
- Community/Regionen (lokale Spenden-/Impact-Kampagnen).
- Creator/Organisatoren (globale Challenges, Events, Kampagnen).

## 5. Feature-Set (modular)

### 5.1 Aufgaben-/Challenge-Typen
- Todo (einmalig)
- Habit/Streak (z. B. 7 Tage abstinent)
- Programm (z. B. 30 Tage)
- Quantified goal (Zahl/Distanz/Geld)
- Team goal (aggregiert)
- Duel (User vs User)
- Team vs Team
- Community/Region goal (Stadt/Land/Verein)
- Global challenge (kuratiert + Erklärung/Story)

### 5.2 Proof (Beweispflicht)
Proof-Methoden (kombinierbar, mit Mindestanforderung):
- SELF: Selbstbestätigung
- PHOTO: Foto
- VIDEO: Video
- DOCUMENT: Datei/Beleg
- PEER: Bestätigung durch andere Person(en)
- SENSOR: Import/Link (Garmin/Strava/Health, später)

Proof-Regeln:
- Deadline für Proof-Upload
- Mindestanzahl Peer-Approvals
- Optional: Plausibilitätschecks (Zeitfenster, Häufigkeit)

### 5.3 Rewards & Progression
- XP/Level, Coins
- Badges/Titel, Cosmetics (UI-Theme/Avatar/Frames)
- Streaks, Milestones, "Grace" (sparsam, transparent)
- Reputation Score (Zuverlässigkeit, Verifizierungshistorie)
- Team-Boni (wenn Team-Ziele eingehalten)

### 5.4 Social & Wettbewerbe
- Invitations (Link, @user, QR)
- Feeds (nur opt-in/konfigurierbar)
- Leaderboards (User/Team/Region)
- Anti-toxicity: private by default, granular controls

### 5.5 Globale Challenges
- Kuratiert: Titel, Beschreibung, Regeln, Zeitraum, optional Partner/Spendenzweck
- Teilnahme offen, Fortschrittsanzeige, Badges
- Optional: Spenden-Uploads oder Provider-Anbindung (später)

## 6. MVP (Version 1) – harte Scope-Grenzen
### Must-have
- Auth (sicher) + Profile
- Teams + Einladungen
- Challenge erstellen (Todo, Streak, Quantified, Team aggregated, Duel)
- Fortschritt tracken (done + numeric contributions)
- Proof: SELF, PHOTO, PEER (mind. 1 Approver)
- Rewards: XP/Level + Streak + einfache Badges
- Leaderboard: Team & Duel
- Notifications: Reminder + Team-Nudges (basic)

### Not in MVP (später)
- SENSOR-Integrationen (Garmin/Strava/Health)
- Zahlungen/Echtgeld-Wetten
- Öffentliche regionale Rankings auf Länder-Ebene (erst später)
- Dispute/Jury-System (nur rudimentär: "flag proof")

## 7. Datenmodell (high level)
### Entities
- User
- Team (Members, Roles)
- Challenge (type, rules, visibility, timeframe, metrics)
- Participation (user/team in challenge)
- Contribution (numeric or done events)
- Proof (type, file refs, metadata, status)
- ProofReview (approvals/rejections by peers)
- RewardEvent (xp/coins/badges)
- Notification (outbox)
- AuditLog (security-critical events)

### Kernbeziehungen
- Challenge has many Participations
- Participation has many Contributions
- Contribution may have Proofs
- Proof has many ProofReviews
- RewardEvents derived from Contributions/Proof status
- AuditLog records: auth, permission changes, proof approvals, admin actions

## 8. Sicherheits- und Compliance-Ansatz (non-negotiable)
- OWASP ASVS-orientiert, OWASP Top 10 mitigations.
- Secure-by-default: private visibility, minimal data retention.
- Least privilege: RBAC/ABAC, scoped permissions.
- Strong auth: MFA-ready, secure sessions, CSRF, rate limits, device management (optional).
- Input validation everywhere; no trust in client.
- File uploads: virus scanning (optional later), content-type sniffing, size limits, signed URLs, isolated storage.
- Secrets: never in repo; env/secret manager; rotation policy.
- Audit logging: immutable-ish (append-only), tamper evidence.
- Dependency security: lockfiles, SCA, CVE scanning in CI.
- Threat modeling: basic model in docs + update on major features.
- Privacy: encryption at rest & in transit, data minimization, user export/delete.

## 9. Tech-Stack (Fixpunkte)
- Frontend: React (TypeScript), modern routing, state mgmt (lean), form validation, accessible UI.
- Backend: Django + Django REST Framework (oder Django Ninja) as API.
- DB: PostgreSQL.
- Cache/Queue: Redis + Celery.
- Storage: S3-compatible (or local dev), signed URLs for uploads.
- Auth: JWT (short-lived) + refresh OR secure cookie sessions; decide early and document.
- Infra: Docker, Compose for dev; CI with GitHub Actions.

## 10. UI/UX – "Apple-like"
- Minimalist, calm, whitespace, clear hierarchy.
- Microinteractions: subtle animations, haptics-like feel (web).
- Predictable navigation; no clutter.
- Strong accessibility: keyboard nav, focus states, contrast, reduced motion.
- "Closed but friendly": guided flows, fewer knobs on primary paths, advanced settings tucked away.

## 11. Repo-Layout (empfohlen, mono-repo)
```
/
  apps/
    web/                # React TS
    api/                # Django
  packages/
    ui/                 # shared UI components (optional)
    shared/             # shared types/schemas (zod/openapi)
  docs/
    SECURITY_REQUIREMENTS.md
    ARCHITECTURE.md
    ADR/                # decision records
  .github/
    workflows/
    copilot-instructions.md
  docker-compose.yml
  Makefile (optional)
```

## 12. Qualitätsziele
- Testpyramide: unit > integration > e2e
- Frontend: component tests + minimal e2e (Playwright)
- Backend: pytest, API contract tests, security tests (rate limit, auth, permissions)
- Observability: structured logs, metrics hooks, error tracking (later)

## 13. Roadmap (kurz)
- MVP: Solo + Team + Duel + Proof (Self/Photo/Peer) + rewards + leaderboard.
- V1+: Templates, global challenges, better notifications.
- V2: Sensor integrations, community/region scale, moderated public challenges.
- V3: AI coach, advanced anti-cheat, partner/spenden integrations.

## 14. Definition of Done (DoD)
- Feature behind permissions/visibility defaults.
- Tests (unit + relevant integration) vorhanden.
- Security checklist applied (input validation, authz, rate limits).
- Docs updated (API schema, ADR if architectural decision).
- UX: responsive, accessible, consistent.
