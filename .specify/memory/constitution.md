# Evolution of Todo Constitution

## Core Principles

### I. Full-Stack Web Development (NON-NEGOTIABLE)
Frontend and backend development must follow established patterns using the designated technology stack; All features must be implemented with both UI and API components; Strict separation of concerns between presentation and business logic layers.

### II. Multi-User System Design
All features must be designed with multi-user considerations from inception; Data isolation mechanisms must prevent cross-user data access; User-specific contexts must be maintained throughout the application lifecycle.

### III. Authentication and Authorization (NON-NEGOTIABLE)
All API endpoints must implement proper authentication and authorization checks; Role-based access control must be enforced consistently; JWT tokens must be validated for all protected resources.

### IV. Database-Backed Persistence
All application state must be persisted to the database; Data integrity constraints must be enforced at the database level; Transactional consistency must be maintained for all operations affecting multiple records.

### V. Monorepo Organization with Spec-Kit Plus
All code must be organized within the monorepo structure following Spec-Kit Plus patterns; Clear separation of frontend and backend packages required; Documentation and specifications must be co-located with relevant code.

### VI. API-Driven Architecture
All backend functionality must be exposed through well-defined APIs; Frontend and backend communication must occur exclusively through API endpoints; API contracts must be versioned and maintained for backward compatibility.

### VII. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced; Both unit and integration tests required for all features.

## Technology Stack Requirements

### Frontend Technologies
Next.js must be used for all frontend development; React components must follow modern patterns and best practices; Client-side rendering and server-side rendering must be appropriately utilized based on use case.

### Backend Technologies
FastAPI must be used for all backend API development; Type hints must be used consistently across all function signatures; Automatic API documentation generation must be enabled.

### Database and ORM
SQLModel ORM must be used for all database interactions; Database schema migrations must be properly managed and versioned; Query optimization must be considered for performance-critical operations.

### Database Infrastructure
Neon Serverless PostgreSQL must be used as the primary database; Connection pooling must be properly configured; Database connection security must follow best practices.

### Authentication System
Better Auth with JWT must be used for all authentication needs; Token refresh mechanisms must be implemented; Secure storage and transmission of authentication data required.

## Development Workflow and Governance

### Spec-Kit Plus Authority Hierarchy
Spec-Kit Plus templates and processes supersede all other development practices; All development must follow the spec-plan-task workflow; Architectural decisions must be documented in ADRs.

### Claude Code Implementation
Claude Code must be the sole implementer of all code changes; No manual coding by humans is permitted; All changes must be traceable through Prompt History Records.

### Phase Isolation
Phase I and Phase II codebases must remain isolated until formal integration; Separate branches and potentially separate repositories must be maintained during active development; Clear boundaries must be maintained between phase-specific features.

### Code Quality and Security
All code must pass security scanning before merging; Static analysis tools must be run on all pull requests; Performance benchmarks must be maintained for critical paths.

## Governance
Constitution supersedes all other practices; Amendments require documentation, approval, and migration plan; All PRs/reviews must verify compliance; Complexity must be justified; Use project documentation for runtime development guidance.

**Version**: 2.0.0 | **Ratified**: 2026-01-20 | **Last Amended**: 2026-01-20
