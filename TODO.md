# CommitQuest – TODO.md

**Stand:** 17. Januar 2026  
**MVP v2 Status:** ✅ 100% Backend, 100% Frontend – Ready for Production

---

## ✅ Abgeschlossen

### Backend
- [x] Django Projektstruktur mit Apps (accounts, challenges, rewards, teams, tasks, core, notifications, debug_feedback)
- [x] Custom User Model mit Avatar, total_points, level, timezone
- [x] JWT Authentifizierung (rest_framework_simplejwt)
- [x] Social Auth Setup (django-allauth + dj-rest-auth für Google, Apple, Facebook)
- [x] Challenge Model mit allen Typen (todo, streak, program, quantified, team, duel, etc.)
- [x] Proof System (Proof, ProofReview Models)
- [x] Contribution Tracking Model
- [x] Reward System (Reward, UserReward, Achievement, UserAchievement, RewardEvent, Streak)
- [x] Team Models (Team, TeamMember, TeamInvitation)
- [x] Audit Logging System (core/audit.py)
- [x] Rate Limiting konfiguriert
- [x] CORS + Security Headers (CORS_ALLOW_ALL_ORIGINS im DEBUG-Modus)
- [x] ALLOWED_HOSTS dynamisch für WLAN-Testing
- [x] API Dokumentation (drf-spectacular)
- [x] Challenges API (ViewSets für Challenges, Contributions, Proofs)
- [x] Rewards API (Badges, Events, Streaks, Progress, Leaderboard)
- [x] Teams API (CRUD, Join/Leave, Invite, Members)
- [x] Tasks API (einfache Todos)
- [x] Database Migrations erstellt und angewendet
- [x] **Gamification Service** (rewards/services.py) – XP, Level, Badges, Streaks
- [x] **Proof Upload Endpoint** – Datei-Upload mit Validierung (Typ, Größe)
- [x] **Proof Review Workflow** – Approve/Reject mit Mindest-Approvals + XP-Vergabe
- [x] **Notifications Model + API** – In-App Notifications mit Preferences
- [x] **Streak-Logik** – update_streak() mit Grace-Perioden, Milestones, Badges
- [x] **Streak Management Command** – `python manage.py check_streaks` für tägliche Prüfung
- [x] **Duel-Logik** – Accept/Decline/Complete mit Gewinner-Ermittlung + XP
- [x] **Credit Economy Backend** – CreditWallet, CreditTransaction, CreditConfig, CreditService
- [x] **Credit Purchase API** – `/api/rewards/credits/add/` für Demo-Kauf
- [x] **Debug Feedback System** – AI-powered QA/Testing mit GPT-4o-mini

### Frontend
- [x] React Projekt Setup
- [x] AuthContext für Login-State
- [x] Login Page
- [x] Register Page (korrigiert: password_confirm)
- [x] Dashboard (Basic + Enhanced mit Sortierung + Zeitkritik)
- [x] API Service Layer (dynamische API-URL für WLAN-Testing)
- [x] **Layout mit Sidebar Navigation** (Layout.js)
- [x] **Dashboard Widgets** (XP Progress, Streaks, Stats, Badges)
- [x] **Challenge Components** (ChallengeCard, ChallengeList, ActiveChallengeMini)
- [x] **Create Challenge Dialog** (Multi-Step Wizard)
- [x] **Proof Components** (PhotoUpload, ProofCard, PendingReviewsList)
- [x] **Leaderboard** (Full + Mini Widget)
- [x] **Enhanced Dashboard** (DashboardNew.js)
- [x] **Challenges Page** (mit Tabs: My, Discover, Active, Completed)
- [x] **Challenge Detail Page** (Fortschritt, Contributions, Leaderboard, Proof Upload)
- [x] **Tasks Page** (mit Create, Filter, Complete)
- [x] **Teams Page** (My Teams, Discover, Create, Join/Leave)
- [x] **Profile Page** (Header, Stats, Badges, Challenges)
- [x] **Leaderboard Page** (Global/Weekly)
- [x] **Navigation/Routing** – react-router-dom mit allen Routes
- [x] **Social Auth Buttons** (Google, Apple, Facebook)
- [x] **OAuth Callback Handler**
- [x] **API Service für Notifications** (notificationService)
- [x] **Notification Center** – Bell Icon mit Dropdown-Menü
- [x] **Toast/Snackbar System** – ToastContext mit useToast Hook
- [x] **Wallet Page** – Credit-Anzeige, Transaktionen, Kostenübersicht
- [x] **Credits Nachkaufen** – Dialog mit Paketen + Custom-Betrag (Demo-Modus)
- [x] **Offene Todos Anzeige** – Dashboard mit Sortierung (Dringlichkeit, Priorität, Fälligkeit)
- [x] **Zeitkritische Tasks** – Visuelle Hervorhebung überfälliger/dringender Tasks
- [x] **Debug Panel** – Floating FAB + Navbar-Icon + Keyboard Shortcut (Ctrl+Shift+D)
- [x] **Voice Memo Recording** – MediaRecorder API für Sprachaufnahmen

### Debug/QA System (NEU)
- [x] **DebugFeedback Model** – Voice/Text Feedback mit AI-Analyse
- [x] **DebugFeedbackService** – GPT-4o-mini für Feedback-Analyse
- [x] **DebugConfig** – Konfiguration mit unlimited_credit_usernames
- [x] **Admin User "crorry"** – Unbegrenzte Credits, voller Debug-Zugriff
- [x] **Debug Panel UI** – Floating Button mit Dialog für Feedback-Eingabe
- [x] **Copilot Instructions** – Optimiert mit Self-Improvement Mandate

### Infrastruktur
- [x] Docker + docker-compose.yml
- [x] GitHub Actions CI (lint, test, security)
- [x] .env.example mit allen Variablen
- [x] Dokumentation (README, ARCHITECTURE, DEVELOPMENT, DEPLOYMENT)

---

## 🔄 In Arbeit

*Keine aktiven Arbeiten - MVP v2 ist 100% fertig!*

---

## ❌ Vor Go-Live empfohlen

### Testen & Qualität
- [x] **API-Tests erweitern** – Tests für Rewards, Teams, Notifications, Challenges erstellt
- [x] **Permission Tests** – Security Tests in core/tests_security.py
- [ ] **E2E Tests** – Playwright Setup für kritische User-Flows (optional für MVP)
- [x] **Security Audit** – OWASP-konforme Security Tests implementiert

### Performance & Skalierung
- [x] **Celery Setup** – taskme_project/celery.py + rewards/tasks.py + notifications/tasks.py
- [x] **Redis Cache** – Konfiguriert mit Fallback auf LocMemCache für Development
- [x] **N+1 Query Optimierung** – select_related/prefetch_related in Views hinzugefügt

---

## 🚀 MVP v2 – Roadmap

### Priorität 1 (nächste 4 Wochen)

#### 💰 Credit & Token-Ökonomie (Core Economy System) ✅ IMPLEMENTIERT
Das Herzstück der App-Wirtschaft – ein deflationäres Punktesystem inspiriert von Krypto-Ökonomien.

**Token-Grundlagen:**
- [x] **Initiales Guthaben** – Neue User erhalten 100 Credits bei Registrierung
- [x] **Credit-Model im Backend** – `CreditWallet`, `CreditTransaction`, `CreditConfig` Models
- [x] **Credit-Balance API** – Endpoints für Balance, Transaktionen, Config, Admin-Management
- [x] **Wallet-UI** – Credit-Anzeige + Wallet-Page mit Historie + Kostenübersicht

**Kosten für Aktionen (Credit Burn):**
- [x] **Challenge erstellen** – Kostet Credits je nach Typ:
  - Simple Todo: 5 Credits
  - Streak Challenge: 10 Credits
  - Quantified Goal: 10 Credits
  - Duel: 15 Credits (Einsatz geht an Gewinner)
  - Team Challenge: 20 Credits
  - Community/Global: 50+ Credits
- [x] **Proof-Anforderungen** – Photo-Proof +5, Video-Proof +10, Peer-Review +3

**Credits Nachkaufen (Demo-Modus implementiert):**
- [x] **Credit-Kauf UI** – Dialog mit 5 Paketen (50-1000 Credits)
- [x] **Custom-Betrag** – Individuelle Menge eingeben
- [x] **Demo-Modus aktiv** – Credits werden direkt gutgeschrieben
- [ ] **Payment Integration** – In-App Purchase (Phase 2, nach MVP)
- [ ] **Pricing-Tiers** – z.B. €4.99 = 100 Credits, €9.99 = 250 Credits

**Belohnungen (Credit Mint):**
- [x] **Todo abschließen** – 3 Credits zurück (konfigurierbar)
- [x] **Challenge bestehen** – 80% der Erstellungskosten zurück
- [x] **Streak-Milestones** – 7 Tage: +10, 30 Tage: +50, 100 Tage: +200 Credits
- [x] **Duel gewinnen** – Erhält eigenen Einsatz + 80% Gegner-Einsatz
- [x] **Badge verdienen** – Bonus-Credits je nach Badge-Seltenheit
- [x] **Peer-Review durchführen** – 1 Credit pro Review

**Ökonomie-Steuerung (Anti-Inflation):**
- [x] **Deflationäres Design** – Mehr Burn als Mint bei Inaktivität
- [ ] **Credit-Verfallsmechanik** – Optional: Inaktive Credits verfallen nach X Monaten
- [x] **Markt-Monitoring** – Admin-Dashboard für Credit-Gesamtmenge im Umlauf
- [ ] **Dynamische Anpassung** – Kosten/Belohnungen basierend auf Marktgröße

**Echtgeld-Integration (Phase 2 - Post-MVP):**
- [ ] **Credit-Kauf** – In-App Purchase für Credits (neue Credits werden "geminted")
- [ ] **Pricing-Tiers** – z.B. €4.99 = 100 Credits, €9.99 = 250 Credits
- [ ] **Charity-Option** – % der Käufe an gemeinnützige Zwecke
- [ ] **Credit-Pool-Transparenz** – Öffentliche Statistik über Gesamtmenge
- [ ] **Premium Features** – Custom Badges, erweiterte Statistiken

**Balance-Beispiel (100 Credits Startguthaben):**
```
Registrierung:                    +100 Credits
Erste Challenge erstellen:         -10 Credits (Streak)
Challenge 7 Tage durchhalten:      +15 Credits (Milestone)
Zweite Challenge erstellen:        -10 Credits
Challenge abgeschlossen:           +12 Credits (Bonus)
3 Peer-Reviews:                     +3 Credits
─────────────────────────────────────────────────
Balance nach 2 Wochen:             110 Credits ✓
```

#### 🎙️ TaskMeMemo – Voice-to-Challenge (Flagship Feature) ✅ IMPLEMENTIERT
- [x] **VoiceMemo Model** – Status-Workflow, Transkription, Parsed-Data, AI-Confidence
- [x] **Sprachaufnahme UI** – Record-Button mit Wellenform-Visualisierung (VoiceRecorder.js)
- [x] **Speech-to-Text Integration** – OpenAI Whisper API in voice_service.py
- [x] **AI Challenge Parser** – GPT-4o-mini analysiert Text und extrahiert:
  - Challenge-Typ (Todo, Streak, Duel, Team, Quantified, Community)
  - Zielwert und Zeitraum
  - Beteiligte Personen/Teams
  - Proof-Typ Empfehlung
- [x] **Original-Memo speichern** – Audio-File wird in VoiceMemo gespeichert
- [x] **Review & Edit Flow** – VoiceMemoDialog mit editierbaren Feldern
- [x] **API Endpoints** – VoiceMemoViewSet mit upload, process, create_challenge, dismiss
- [x] **Frontend Integration** – VoiceMemoButton im Dashboard
- [x] **Cost Integration** – CostIndicator zeigt Credits vor Erstellung
- [ ] **Feedback-Loop für ML** – User-Korrekturen speichern für Modell-Verbesserung (optional)
- **Beispiel-Prompts funktionieren:**
  - *"Du schaffst es nie zwei Wochen keinen Alkohol zu trinken"* → Streak Challenge, 14 Tage
  - *"Ich möchte 30 Tage jeden Tag 10 km laufen"* → Quantified, 30×10km
  - *"Wir möchten als Team ein anderes Team herausfordern..."* → Team vs Team Duel

#### UX Verbesserungen
- [ ] **Dark Mode** – Theme Toggle mit System-Präferenz
- [ ] **Responsive Optimierung** – Mobile-first Audit aller Seiten
- [ ] **Accessibility Audit** – WCAG 2.1 AA Konformität (Keyboard, ARIA, Kontrast)
- [ ] **Onboarding Flow** – Tutorial für neue User (3-5 Screens)
- [ ] **Empty States** – Schöne Illustrations wenn keine Daten

#### Challenge Features
- [ ] **Challenge Templates** – Vordefinierte populäre Challenges
- [ ] **Challenge Categories** – Fitness, Learning, Habits, Productivity
- [ ] **Team-Aggregierte Challenges** – Team-Punkte summieren
- [ ] **Challenge Comments** – Kommentare auf Contributions

#### Notifications
- [ ] **Push Notifications** – Web Push API Integration
- [ ] **Email Notifications** – Wöchentliche Summaries
- [ ] **Streak Reminder** – Tägliche Push wenn Streak gefährdet

### Priorität 2 (Wochen 5-8)

#### Sensor-Integrationen
- [ ] **Strava Connect** – Automatische Activity-Imports
- [ ] **Garmin Connect** – Fitness-Daten Import
- [ ] **Apple Health** – iOS Health Import (Schritte, Workouts)
- [ ] **Google Fit** – Android Health Import

#### Social Features
- [ ] **User Search** – Nach Username/Name suchen
- [ ] **Follow/Friends** – Freundesliste führen
- [ ] **Activity Feed** – Was machen meine Freunde?
- [ ] **Share Challenge** – Social Media Sharing

#### Gamification Erweiterungen
- [ ] **Seasonal Challenges** – Zeitlich begrenzte Global Events
- [ ] **Achievement System** – Mehr Badges + Achievement-Tracking
- [ ] **Level Perks** – Freischaltbare Features pro Level
- [ ] **Weekly Challenges** – Automatisch generierte wöchentliche Goals

### Priorität 3 (Post-Launch Features)

#### Advanced Features
- [ ] **Video-Proof Support** – Video-Upload mit Thumbnail
- [ ] **AI Coach** – Motivation, Tipps, personalisierte Vorschläge
- [ ] **Advanced Anti-Cheat** – ML-basierte Plausibilitätsprüfung
- [ ] **Community Moderation** – Report/Block Funktionen

#### Monetarisierung
- [ ] **Premium Features** – Erweiterte Statistiken, Custom Badges
- [ ] **Team-Subscriptions** – Pro-Teams mit erweiterten Features
- [ ] **Charity-Partner-Integration** – Challenges für guten Zweck

---

## 🛠 Technische Schulden

### Code-Qualität
- [ ] **TypeScript Migration** – Schrittweise Konvertierung aller Components
- [ ] **Error Handling standardisieren** – Einheitliche Error-Response-Struktur
- [ ] **Logging verbessern** – Request-IDs durchgängig
- [ ] **OpenAPI Schema** – Generieren und versionieren
- [ ] **Frontend Design System** – Komponenten-Bibliothek

### DevOps
- [ ] **Staging Environment** – Separate Staging-Umgebung aufsetzen
- [ ] **Blue-Green Deployment** – Zero-Downtime Deployments
- [ ] **Monitoring** – Sentry Error Tracking, APM
- [ ] **Load Testing** – Performanz-Tests vor Go-Live

---

## 🔑 Umgebungsvariablen für Social Auth

Folgende Variablen müssen in `.env` gesetzt werden:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Apple OAuth  
APPLE_CLIENT_ID=your-apple-service-id
APPLE_CLIENT_SECRET=your-apple-client-secret
APPLE_KEY_ID=your-apple-key-id
APPLE_CERTIFICATE_KEY=-----BEGIN PRIVATE KEY-----...

# Facebook OAuth
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

Die OAuth-Apps müssen in den jeweiligen Developer Consoles erstellt werden:
- Google: https://console.cloud.google.com/
- Apple: https://developer.apple.com/
- Facebook: https://developers.facebook.com/

---

## 📊 API Endpoints Übersicht

### Auth
- `POST /api/auth/register/` – Registrierung
- `POST /api/auth/login/` – Login (JWT)
- `POST /api/auth/token/refresh/` – Token erneuern
- `GET /api/auth/profile/` – Eigenes Profil
- `GET /api/auth/social/` – Social Auth (allauth)

### Challenges
- `GET/POST /api/challenges/` – Liste/Erstellen
- `GET/PATCH/DELETE /api/challenges/{id}/` – Detail
- `POST /api/challenges/{id}/join/` – Beitreten
- `GET /api/challenges/{id}/leaderboard/` – Challenge-Rangliste
- `GET /api/contributions/` – Eigene Beiträge
- `POST /api/contributions/` – Beitrag hinzufügen
- `GET/POST /api/proofs/` – Beweise
- `POST /api/proofs/{id}/review/` – Review abgeben

### Rewards
- `GET /api/rewards/badges/` – Alle Badges
- `GET /api/rewards/badges/earned/` – Eigene Badges
- `GET /api/rewards/events/` – XP-History
- `GET /api/rewards/streaks/` – Aktive Streaks
- `GET /api/rewards/progress/` – Fortschritts-Übersicht
- `GET /api/rewards/leaderboard/` – Rangliste

### Teams
- `GET/POST /api/teams/` – Liste/Erstellen
- `GET/PATCH/DELETE /api/teams/{id}/` – Detail
- `POST /api/teams/{id}/join/` – Beitreten
- `POST /api/teams/{id}/leave/` – Verlassen
- `GET /api/teams/{id}/members/` – Mitglieder
- `POST /api/teams/{id}/invite/` – Einladen
- `GET /api/teams/my_teams/` – Eigene Teams

### Tasks (Simple Todos)
- `GET/POST /api/tasks/` – Liste/Erstellen
- `GET/PATCH/DELETE /api/tasks/{id}/` – Detail
- `POST /api/tasks/{id}/complete/` – Abschließen

### Notifications (NEU)
- `GET /api/notifications/` – Liste
- `GET /api/notifications/unread_count/` – Ungelesene Anzahl
- `POST /api/notifications/{id}/mark_read/` – Als gelesen markieren
- `POST /api/notifications/mark_all_read/` – Alle als gelesen
- `GET /api/notifications/preferences/` – Einstellungen
- `PATCH /api/notifications/preferences/` – Einstellungen ändern

---

*Letztes Update: 16. Januar 2026*
