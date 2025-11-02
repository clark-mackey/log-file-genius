# Development Log - Task Management API

A narrative chronicle of the project journey - the decisions, discoveries, and pivots that shaped the work.

---

## Related Documents

📋 **[PRD](../../specs/PRD.md)** - Product requirements and specifications  
📊 **[CHANGELOG](CHANGELOG.md)** - Technical changes and version history  
📐 **[ADRs](adr/README.md)** - Architectural decision records  
🔄 **[STATE](STATE.md)** - Current project state and active work

> **For AI Agents:** This file tells the story of *why* decisions were made. Before starting work, read **Current Context** and **Decisions (ADR)** sections. For technical details of *what* changed, see CHANGELOG.md.

---

## Current Context (Source of Truth)

**Last Updated:** 2025-10-28

### Project State
- **Project:** Task Management API
- **Current Version:** v0.4.0-dev
- **Active Branch:** `feature/websocket-pooling`
- **Phase:** Beta (real-time features in testing)

### Stack & Tools
- **Backend:** Python 3.11, FastAPI 0.104, Uvicorn
- **Database:** PostgreSQL 15 with full-text search
- **Real-time:** WebSocket (native FastAPI support)
- **Auth:** JWT with refresh tokens (Argon2id password hashing)
- **Deployment:** Docker, Railway (staging), AWS (production planned)
- **Testing:** pytest, coverage >85% required

### Standards & Conventions
- **Code Style:** `black` (Python), `isort` (imports)
- **Commits:** Conventional Commits format
- **Decisions:** ADRs required for architectural choices
- **Testing:** All new features require tests before merge
- **API:** RESTful v1, follows RFC 7807 for errors

### Key Architectural Decisions
- **ADR-003 (2025-10-27):** Optimistic Locking for Task Updates [→ Full ADR](adr/003-optimistic-locking.md)
- **ADR-002 (2025-10-21):** JWT Authentication with Refresh Tokens [→ Full ADR](adr/002-jwt-authentication.md)
- **ADR-001 (2025-10-15):** PostgreSQL Over MongoDB [→ Full ADR](adr/001-postgresql-choice.md)

### Constraints & Requirements
- **Performance:** P95 latency < 200ms for API endpoints, < 100ms for WebSocket messages
- **Security:** All endpoints require authentication except `/health` and `/docs`
- **Data:** Soft deletes only, never hard delete user data
- **Compatibility:** Support mobile apps (iOS/Android) via REST + WebSocket

### Current Objectives (Week of Oct 27)
- [x] Fix WebSocket memory leak (v0.3.2)
- [x] Implement optimistic locking for task updates (v0.3.1)
- [ ] Complete WebSocket connection pooling (v0.4.0)
- [ ] Add bulk task operations endpoint (v0.4.0)
- [ ] Performance testing with 1000+ concurrent WebSocket connections

### Known Risks & Blockers
- **Risk:** WebSocket connection pooling may not scale beyond 5000 concurrent connections. Need to test with load testing tools.
- **Risk:** Database query performance degrading with >100k tasks per user. May need partitioning strategy.
- **Blocker:** Mobile app team waiting for bulk operations endpoint before starting sync feature.

### Entry Points (For Code Navigation)
- **Backend Main:** `src/main.py`
- **API Routes:** `src/api/v1/`
- **WebSocket Manager:** `src/websocket/manager.py`
- **Database Models:** `src/models/`
- **Database Schema:** `migrations/`

---

## Decisions (ADR Index) - Newest First

- **ADR-003 (2025-10-27):** Optimistic Locking for Task Updates - Use version field to prevent race conditions [→ Full ADR](adr/003-optimistic-locking.md)
- **ADR-002 (2025-10-21):** JWT Authentication with Refresh Tokens - Replace session-based auth for mobile support [→ Full ADR](adr/002-jwt-authentication.md)
- **ADR-001 (2025-10-15):** PostgreSQL Over MongoDB - Choose relational DB for data integrity [→ Full ADR](adr/001-postgresql-choice.md)

---

## Daily Log - Newest First

### 2025-10-28: The WebSocket Memory Leak Hunt

**The Problem:** Production monitoring showed memory usage climbing steadily over 24 hours, eventually causing the server to crash. Memory profiling pointed to WebSocket connections not being released.

**The Investigation:** Added detailed logging to WebSocket connection lifecycle. Discovered that when clients disconnected abruptly (network issues, app crashes), the `disconnect` event wasn't firing reliably. Connections stayed in the `active_connections` dictionary forever, holding references to user sessions and database connections.

**The Root Cause:** We were relying solely on the WebSocket `disconnect` event, but FastAPI doesn't guarantee this event fires for all disconnection scenarios (especially network timeouts).

**The Solution:** Implemented a heartbeat mechanism - clients must send a ping every 30 seconds, server removes connections that haven't pinged in 60 seconds. Added a background task that runs every minute to clean up stale connections.

**The Result:** Memory usage now stable over 48+ hours. Stale connections cleaned up within 60 seconds of client disconnect. Added monitoring alerts for connection count anomalies.

**Files Changed:** `src/websocket/manager.py`, `src/websocket/heartbeat.py`, `tests/test_websocket_cleanup.py`

**Shipped:** v0.3.2

---

### 2025-10-27: Race Conditions and Optimistic Locking

**The Situation:** Users reported task updates being lost when multiple team members edited the same task simultaneously. User A's changes would overwrite User B's changes with no warning.

**The Challenge:** Classic race condition - two requests read the same task state, make different changes, both write back. Last write wins, first write is lost silently.

**The Investigation:** Considered several solutions: pessimistic locking (lock row during read), optimistic locking (version field), or event sourcing (append-only log). Pessimistic locking would hurt performance for the common case (no conflicts). Event sourcing was overkill for our needs.

**The Decision:** Implemented optimistic locking with a `version` field. Every task update increments the version. If the version in the update request doesn't match the current version, we return a 409 Conflict error with the current task state. This is documented in ADR-003.

**Why This Works:** Most updates don't conflict (different tasks or different times). When conflicts do occur, users get immediate feedback and can merge changes manually. No performance penalty for the common case.

**The Implementation:** Added `version` integer field to tasks table, updated all update endpoints to check version, added conflict resolution UI guidance in API docs.

**Files Changed:** `src/models/task.py`, `src/api/v1/tasks.py`, `migrations/007_add_version_field.sql`, `tests/test_optimistic_locking.py`

**Shipped:** v0.3.1

---

### 2025-10-25: Real-Time Updates - The WebSocket Journey

**The Context:** Users wanted to see task updates in real-time without refreshing. Initial plan was polling (client requests updates every 5 seconds), but that's inefficient and creates lag.

**The Realization:** WebSocket support in FastAPI is mature and well-documented. Real-time updates would be a major UX improvement and differentiate us from competitors still using polling.

**The Decision:** Implement WebSocket-based real-time updates. When any task changes (create, update, delete), broadcast the change to all connected clients who have access to that task.

**The Challenge:** WebSocket authentication. HTTP endpoints use JWT in Authorization header, but WebSocket connections can't send custom headers in browser JavaScript. Options: send token in query parameter (insecure, logged in URLs), send token in first message (complex handshake), or use cookie-based auth (requires CSRF protection).

**The Solution:** Hybrid approach - accept JWT in query parameter for initial connection (validated immediately, not logged), then switch to message-based auth for subsequent frames. Connection is closed if auth fails within 5 seconds.

**The Implementation:** Created WebSocket manager to track connections, implemented pub/sub pattern for broadcasting updates, added authentication middleware for WebSocket connections.

**The Result:** Real-time updates working smoothly. Latency from task update to client notification is <50ms. Deprecated the polling endpoint for removal in v0.5.0.

**Files Changed:** `src/websocket/manager.py`, `src/websocket/auth.py`, `src/websocket/events.py`, `src/api/v1/tasks.py`

**Shipped:** v0.3.0

---

### 2025-10-21: The Authentication Pivot - Sessions to JWT

**The Problem:** We had built session-based authentication (cookies, server-side session storage), but the mobile app team couldn't use it. Mobile apps need token-based auth, not cookies.

**The Dilemma:** Rewrite authentication to support both sessions (web) and tokens (mobile)? Or pick one approach and use it everywhere?

**The Research:** Investigated how other APIs handle this. Most modern APIs use JWT exclusively - simpler, stateless, works everywhere. Sessions are legacy for APIs, though still common for traditional web apps.

**The Decision:** Migrate from session-based to JWT-based authentication with refresh tokens. This is documented in ADR-002. Short-lived access tokens (15 minutes) with long-lived refresh tokens (30 days) for security.

**The Tradeoff:** Lost the ability to instantly revoke sessions (JWT can't be revoked until expiry). Mitigated by short access token lifetime and refresh token rotation (each refresh issues new token and invalidates old one).

**The Migration:** Implemented JWT generation and validation, added refresh token endpoint, migrated password hashing from bcrypt to Argon2id (more secure, better for JWT use case), updated all API endpoints to validate JWT instead of sessions.

**The Result:** Mobile app team unblocked. Web app switched to JWT (stored in httpOnly cookies for security). Authentication is now stateless and scalable.

**Files Changed:** `src/auth/*.py`, `src/api/middleware/auth.py`, `src/models/refresh_token.py`, `migrations/005_jwt_migration.sql`

**Shipped:** v0.2.3

---

### 2025-10-19: Search Performance - The Indexing Revelation

**The Situation:** Task search was working but slow. With 10k+ tasks in the database, search queries were taking 2-3 seconds. Users expected instant results.

**The Investigation:** Analyzed query execution plans. The search was doing full table scans with `LIKE '%query%'` on title and description fields. No indexes could help with leading wildcard searches.

**The Discovery:** PostgreSQL has built-in full-text search with GIN indexes. It's faster than `LIKE` queries and supports ranking, stemming, and relevance scoring. We didn't need Elasticsearch for our use case.

**The Implementation:** Created `tsvector` column combining title and description, added GIN index on the tsvector, updated search endpoint to use `@@` operator instead of `LIKE`.

**The Result:** Search queries now complete in <50ms even with 100k+ tasks. Bonus: we got relevance ranking for free, so most relevant results appear first.

**The Lesson:** PostgreSQL has powerful features beyond basic SQL. Always check built-in capabilities before adding external dependencies.

**Files Changed:** `src/api/v1/search.py`, `migrations/004_search_indexes.sql`, `tests/test_search_performance.py`

**Shipped:** v0.2.2

---

### 2025-10-15: Authentication - The Security Foundation

**The Context:** MVP launched without authentication - anyone could create/edit/delete any task. This was fine for initial testing but not viable for real users.

**The Challenge:** Add authentication without breaking existing API clients or requiring a full rewrite. Also needed to associate existing tasks with users.

**The Approach:** Implemented email/password authentication with secure session cookies. Added `user_id` foreign key to tasks table. For existing tasks (created before auth), assigned them to a special "anonymous" user account.

**The Security Decisions:** 
- Argon2id for password hashing (more secure than bcrypt)
- CSRF protection for session cookies
- Rate limiting (100 requests/minute per user)
- Secure session cookies (httpOnly, sameSite=strict)

**The Migration:** Created users table, added authentication endpoints, updated all task endpoints to require auth and filter by user_id, migrated existing tasks to anonymous user.

**The Result:** Secure multi-user system. Each user sees only their own tasks. Foundation for future features like task sharing and team collaboration.

**Files Changed:** `src/auth/handlers.py`, `src/models/user.py`, `src/api/v1/users.py`, `src/api/middleware/csrf.py`, `migrations/002_add_user_id.sql`

**Shipped:** v0.2.0

---

### 2025-10-09: Project Launch - Building the Foundation

**The Vision:** Create a modern task management API that's fast, reliable, and easy to integrate with mobile and web apps.

**The Stack Decision:** Chose FastAPI for its performance, automatic API docs, and excellent async support. PostgreSQL for data integrity and powerful querying. Docker for consistent development and deployment.

**The MVP Scope:** Basic CRUD operations for tasks (create, read, update, delete), health check endpoint for monitoring, database migrations for schema management.

**The Architecture:** Clean separation of concerns - API layer (routes), business logic (services), data layer (models), database (migrations). This structure would scale as the project grew.

**The First Week:** Set up project structure, implemented task CRUD endpoints, created database schema, added Docker configuration for local development, wrote initial tests.

**The Result:** Working MVP deployed to staging. Could create, list, update, and delete tasks via REST API. Foundation ready for authentication, search, and real-time features.

**Files Changed:** `src/main.py`, `src/api/v1/tasks.py`, `src/models/task.py`, `migrations/001_initial_schema.sql`, `Dockerfile`, `docker-compose.yml`

**Shipped:** v0.1.0

---

## Archive

**Entries older than 14 days** are archived for token efficiency:
- No archived entries yet (project started October 2025)

