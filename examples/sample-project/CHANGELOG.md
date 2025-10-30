# Changelog - Task Management API

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Related Documents

📋 **[PRD](../../specs/PRD.md)** - Product requirements and specifications  
📖 **[DEVLOG](DEVLOG.md)** - Development narrative and decision rationale  
📐 **[ADRs](adr/README.md)** - Architectural decision records  
🔄 **[STATE](STATE.md)** - Current project state and active work

> **For AI Agents:** This file is a concise technical record of changes. For context on *why* decisions were made, see DEVLOG.md. For current project state, see STATE.md.

---

## [Unreleased] - v0.4.0-dev

### Added
- WebSocket connection pooling - Reuse connections for better performance. Files: `src/websocket/pool.py`. PR: [#89](link)
- Task assignment notifications - Real-time alerts when tasks are assigned. Files: `src/notifications/task_events.py`. PR: [#90](link)

### Changed
- Database connection pool size - Increased from 10 to 25 for better concurrency. Files: `src/database/config.py`. PR: [#88](link)

---

## [0.3.2] - 2025-10-28

### Added
- Bulk task operations endpoint - Create/update/delete multiple tasks in one request. Files: `src/api/v1/tasks.py`, `src/services/bulk_operations.py`. PR: [#85](link)
- Task filtering by priority - Query parameter `?priority=high,medium,low`. Files: `src/api/v1/tasks.py`. PR: [#86](link)

### Fixed
- WebSocket memory leak - Connections not properly closed on client disconnect. Files: `src/websocket/manager.py`. PR: [#87](link)

---

## [0.3.1] - 2025-10-27

### Fixed
- Database query performance - Added index on `tasks.user_id` and `tasks.status`. Files: `migrations/007_add_task_indexes.sql`. PR: [#82](link)
- Task update race condition - Implemented optimistic locking with version field. Files: `src/models/task.py`, `src/api/v1/tasks.py`. PR: [#83](link)

### Changed
- Error response format - Standardized to RFC 7807 Problem Details. Files: `src/api/middleware/error_handler.py`. PR: [#84](link)

---

## [0.3.0] - 2025-10-25

### Added
- Real-time task updates via WebSocket - Clients receive live updates when tasks change. Files: `src/websocket/manager.py`, `src/websocket/events.py`. PR: [#75](link)
- WebSocket authentication - JWT token validation for WebSocket connections. Files: `src/websocket/auth.py`. PR: [#76](link)
- Task activity log - Track all changes to tasks with timestamps and user info. Files: `src/models/task_activity.py`, `migrations/006_task_activity.sql`. PR: [#77](link)

### Changed
- Task update endpoint - Now broadcasts changes via WebSocket to connected clients. Files: `src/api/v1/tasks.py`. PR: [#78](link)

### Deprecated
- Polling endpoint `/api/v1/tasks/poll` - Use WebSocket connection instead. Removal planned for v0.5.0. Migration: [docs/websocket-migration.md](link)

---

## [0.2.4] - 2025-10-23

### Added
- Task comments API - CRUD operations for task comments. Files: `src/api/v1/comments.py`, `src/models/comment.py`. PR: [#70](link)
- Comment notifications - Email notifications when users are mentioned in comments. Files: `src/notifications/comment_mentions.py`. PR: [#71](link)

### Fixed
- JWT token refresh race condition - Tokens could be refreshed multiple times simultaneously. Files: `src/auth/token_manager.py`. PR: [#72](link)

---

## [0.2.3] - 2025-10-21

### Added
- Task due date reminders - Background job sends email 24h before due date. Files: `src/jobs/reminder_scheduler.py`. PR: [#65](link)
- User preferences API - Store notification and display preferences. Files: `src/api/v1/preferences.py`, `src/models/user_preferences.py`. PR: [#66](link)

### Changed
- Authentication flow - Switched from session-based to JWT with refresh tokens per ADR-002. Files: `src/auth/*.py`, `src/api/middleware/auth.py`. PR: [#67](link)

### Security
- Password hashing - Migrated from bcrypt to Argon2id for better security. Files: `src/auth/password.py`, `migrations/005_rehash_passwords.sql`. PR: [#68](link)

---

## [0.2.2] - 2025-10-19

### Added
- Task search endpoint - Full-text search across task titles and descriptions. Files: `src/api/v1/search.py`. PR: [#60](link)
- Search indexing - PostgreSQL full-text search with GIN index. Files: `migrations/004_search_indexes.sql`. PR: [#61](link)

### Fixed
- Task list pagination - Cursor-based pagination to prevent skipped/duplicate items. Files: `src/api/v1/tasks.py`. PR: [#62](link)

---

## [0.2.1] - 2025-10-17

### Added
- Task tags - Many-to-many relationship for flexible categorization. Files: `src/models/tag.py`, `migrations/003_task_tags.sql`. PR: [#55](link)
- Tag management API - CRUD operations for tags. Files: `src/api/v1/tags.py`. PR: [#56](link)

### Changed
- Task priority field - Changed from integer (1-5) to enum (low, medium, high, urgent). Files: `src/models/task.py`, `migrations/003_priority_enum.sql`. PR: [#57](link)

---

## [0.2.0] - 2025-10-15

### Added
- User authentication - Email/password registration and login. Files: `src/auth/handlers.py`, `src/models/user.py`. PR: [#45](link)
- Session management - Secure session cookies with CSRF protection. Files: `src/auth/session.py`, `src/api/middleware/csrf.py`. PR: [#46](link)
- User profile API - Get/update user profile information. Files: `src/api/v1/users.py`. PR: [#47](link)

### Changed
- Task model - Added `user_id` foreign key to associate tasks with users. Files: `src/models/task.py`, `migrations/002_add_user_id.sql`. PR: [#48](link)
- API endpoints - All task endpoints now require authentication. Files: `src/api/v1/tasks.py`. PR: [#49](link)

### Security
- Rate limiting - Implemented per-user rate limits (100 req/min). Files: `src/api/middleware/rate_limit.py`. PR: [#50](link)

---

## [0.1.2] - 2025-10-13

### Added
- Task status transitions - Validate state changes (todo → in_progress → done). Files: `src/models/task.py`. PR: [#40](link)
- Task assignment - Assign tasks to users (placeholder for future auth). Files: `src/models/task.py`. PR: [#41](link)

### Fixed
- Task creation validation - Reject tasks with empty titles or invalid dates. Files: `src/api/v1/tasks.py`. PR: [#42](link)

---

## [0.1.1] - 2025-10-11

### Added
- Task list endpoint - GET /api/v1/tasks with pagination. Files: `src/api/v1/tasks.py`. PR: [#30](link)
- Task filtering - Filter by status, priority, due date. Files: `src/api/v1/tasks.py`. PR: [#31](link)

### Fixed
- Database connection leak - Properly close connections in error cases. Files: `src/database/connection.py`. PR: [#32](link)

---

## [0.1.0] - 2025-10-09

### Added
- Initial project setup - FastAPI application with basic structure. Files: `src/main.py`, `src/api/router.py`. PR: [#1](link)
- Database schema - PostgreSQL schema for tasks table. Files: `migrations/001_initial_schema.sql`. PR: [#2](link)
- Task CRUD API - Create, read, update, delete tasks. Files: `src/api/v1/tasks.py`, `src/models/task.py`. PR: [#3](link)
- Health check endpoint - GET /health for monitoring. Files: `src/api/health.py`. PR: [#4](link)
- Docker setup - Dockerfile and docker-compose for local development. Files: `Dockerfile`, `docker-compose.yml`. PR: [#5](link)

---

## Archive

**Versions older than 30 days** are archived for token efficiency:
- No archived versions yet (project started October 2025)

