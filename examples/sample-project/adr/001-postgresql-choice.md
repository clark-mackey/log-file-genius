# ADR-001: PostgreSQL Over MongoDB

**Status:** Accepted  
**Date:** 2025-10-15  
**Deciders:** Engineering team (Agent-1, Developer-1)  
**Related:** Issue #10, PR #15

---

## Context

We need to choose a database for the Task Management API. The core data model includes tasks with structured fields (title, description, status, priority, due date, assignee) and relationships (users own tasks, tasks have comments, tasks have tags).

Key requirements:
- **Data integrity:** Tasks must maintain referential integrity with users
- **Query flexibility:** Need to filter tasks by multiple criteria (status, priority, assignee, tags, due date)
- **Performance:** Must support 100k+ tasks per user with sub-200ms query times
- **Future features:** Planned features include task sharing, team workspaces, and activity logs

The team debated between PostgreSQL (relational) and MongoDB (document-oriented). MongoDB was appealing for its flexibility and JSON-like documents, but we had concerns about data integrity and complex queries.

---

## Decision

We will use **PostgreSQL 15** as the primary database for the Task Management API.

All data will be stored in normalized relational tables with foreign key constraints. We will use PostgreSQL's JSON/JSONB columns for truly flexible data (like task metadata or custom fields) while keeping core fields in typed columns.

---

## Consequences

### Positive

- **Data integrity:** Foreign key constraints prevent orphaned tasks and invalid references
- **Query power:** Complex joins and filters are straightforward with SQL
- **ACID guarantees:** Transactions ensure consistency for multi-step operations
- **Rich features:** Full-text search, JSON support, array types, and powerful indexing
- **Mature ecosystem:** Well-understood, excellent tooling, strong community support
- **Cost-effective:** Can run on smaller instances due to efficient query planning

### Negative

- **Schema migrations:** Changes to table structure require migrations (though we're using Alembic to manage this)
- **Learning curve:** Team members unfamiliar with SQL need to learn it
- **Horizontal scaling:** More complex than MongoDB (though vertical scaling is sufficient for our scale)

### Neutral

- **ORM choice:** Will use SQLAlchemy for Python ORM, which is mature but adds abstraction layer
- **Backup strategy:** Need to implement regular pg_dump backups (standard practice)

---

## Alternatives Considered

### Alternative 1: MongoDB

**Pros:**
- Flexible schema (no migrations needed)
- Horizontal scaling is easier
- JSON-native storage matches API responses

**Rejected because:**
- No foreign key constraints - data integrity must be enforced in application code
- Complex queries (multi-field filters, joins) are harder to write and optimize
- Transactions are more limited (though improved in recent versions)
- Team has more PostgreSQL experience than MongoDB
- Our data model is inherently relational (users → tasks → comments → tags)

### Alternative 2: MySQL

**Pros:**
- Similar to PostgreSQL in most ways
- Slightly simpler for basic use cases

**Rejected because:**
- PostgreSQL has better JSON support (JSONB type with indexing)
- PostgreSQL has superior full-text search (we need this for task search)
- PostgreSQL has more advanced features we may need later (array types, window functions)
- Team prefers PostgreSQL's standards compliance

### Alternative 3: SQLite

**Pros:**
- Extremely simple setup
- No separate database server needed
- Perfect for development

**Rejected because:**
- Not suitable for production multi-user applications
- Limited concurrency support
- No network access (can't scale to multiple app servers)
- Good for development/testing, but we'd still need PostgreSQL for production

---

## Notes

- We'll use PostgreSQL 15 for its improved performance and JSON features
- Database will be hosted on managed service (Railway for staging, AWS RDS for production)
- Connection pooling will be handled by SQLAlchemy with pool size tuned based on load testing
- We'll use Alembic for schema migrations to make changes trackable and reversible
- Full-text search will use PostgreSQL's built-in capabilities (GIN indexes on tsvector columns)

**Implementation:**
- Initial schema created in migration `001_initial_schema.sql`
- SQLAlchemy models defined in `src/models/`
- Database connection configuration in `src/database/connection.py`

**References:**
- PostgreSQL documentation: https://www.postgresql.org/docs/15/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- Discussion in Issue #10 about database choice

