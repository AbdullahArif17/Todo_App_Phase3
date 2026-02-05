<!-- SYNC IMPACT REPORT
Version change: 2.0.0 → 3.0.0
Modified principles: Completely revised to focus on AI Chatbot Todo application
Added sections: AI Agent Rules, Statelessness, Tool-First Development, Deterministic Behavior
Removed sections: Previous principles about multi-user system, authentication, etc. (replaced with AI-focused principles)
Templates requiring updates: ✅ Updated all relevant templates
Follow-up TODOs: None
-->

# Project Constitution – Phase III (Todo AI Chatbot)

## Version: 3.0.0 | Ratified: 2026-01-20 | Last Amended: 2026-02-03

## Purpose
Build a stateless, scalable AI-powered Todo chatbot that manages tasks via natural language using MCP tools and AI agents.

## Core Principles

### I. Spec-Driven Only (NON-NEGOTIABLE)
All behavior must be defined in specifications; No manual coding by humans is permitted; All implementation must follow the spec-plan-task workflow defined in Spec-Kit Plus; Deviations from the spec require formal amendment procedures.

### II. Stateless Backend (NON-NEGOTIABLE)
No in-memory state must be maintained between requests; All application state must be persisted in the database; The system must be horizontally scalable without shared memory; Session state must be stored in persistent storage or derived from authentication tokens.

### III. Tool-First AI Development (NON-NEGOTIABLE)
The AI agent must only modify data through MCP tools; Direct database manipulation outside of tools is prohibited; All operations must be logged and traceable through tool calls; The AI must never hallucinate task state or rely on in-memory caches.

### IV. Deterministic Behavior (NON-NEGOTIABLE)
Identical input with identical database state must produce identical outcomes; All operations must be idempotent where applicable; Randomness must be eliminated from core business logic; Conversations must be replayable from database state alone.

### V. Security First Approach (NON-NEGOTIABLE)
All actions must be scoped to authenticated users; Data access must be validated through proper authentication and authorization; User data isolation must be maintained at all system layers; Secrets must be stored securely and never hardcoded.

### VI. Scalability Ready Architecture
Design must support horizontal scaling from inception; Database queries must be optimized for concurrent access; Resource usage must be monitored and bounded; System must handle load increases gracefully without architectural changes.

### VII. Clear User Experience
Every AI action must be confirmed in natural language; User intent must be explicitly verified before executing operations; Error messages must be clear and actionable; System state changes must be communicated transparently to users.

### VIII. Graceful Failure Handling
Errors must be handled without breaking conversations; Fallback mechanisms must be in place for all critical operations; Error states must be logged for debugging purposes; Users must receive informative feedback during failures.

## AI Agent Rules

### IX. MCP Tool Compliance (NON-NEGOTIABLE)
AI agents must never hallucinate task state; Always call MCP tools for task operations; Ask for clarification only when required by business logic; Chain tools when needed (e.g., list → delete) to accomplish complex operations.

### X. Natural Language Processing
AI must interpret natural language input consistently; Intent recognition must be reliable and predictable; Ambiguous requests must trigger clarification rather than assumptions; Response formatting must follow established patterns.

## Quality Standards

### XI. Clean Architecture Separation (NON-NEGOTIABLE)
Clear separation required between UI, API, Agent, MCP, and Database layers; Each layer must have well-defined responsibilities; Cross-layer dependencies must be minimized and explicit; Interface contracts must be maintained for stability.

### XII. Observability and Logging (NON-NEGOTIABLE)
Clear logging of all tool calls must be maintained; System state changes must be traceable through logs; Performance metrics must be collected for all critical paths; Audit trails must be available for all user actions.

### XIII. Conversation Integrity (NON-NEGOTIABLE)
Conversations must be replayable from database records alone; Message ordering and context must be preserved; Conversation state must survive system restarts; Historical conversation data must remain accessible.

### XIV. Restart-Safe Operations (NON-NEGOTIABLE)
System must recover gracefully from unexpected shutdowns; No memory loss must occur during restarts; In-progress operations must either complete or rollback safely; Data consistency must be maintained during restarts.

## Technology Stack Requirements

### XV. Backend Technologies
FastAPI must be used for all backend API development; Type hints must be used consistently across all function signatures; Automatic API documentation generation must be enabled; Async operations must be properly implemented for scalability.

### XVI. Database and ORM
SQLModel ORM must be used for all database interactions; Database schema migrations must be properly managed and versioned; Query optimization must be considered for performance-critical operations; Connection pooling must be properly configured.

### XVII. Database Infrastructure
Neon Serverless PostgreSQL must be used as the primary database; Database connection security must follow best practices; Data retention policies must be implemented appropriately; Backup and recovery procedures must be in place.

### XVIII. Frontend Technologies
Next.js must be used for all frontend development; React components must follow modern patterns and best practices; Client-side rendering and server-side rendering must be appropriately utilized based on use case; Real-time updates must be implemented efficiently.

## Development Workflow and Governance

### XIX. Spec-Kit Plus Authority Hierarchy (NON-NEGOTIABLE)
Spec-Kit Plus templates and processes supersede all other development practices; All development must follow the spec-plan-task workflow; Architectural decisions must be documented in ADRs; Prompt History Records must be created for all significant changes.

### XX. Claude Code Implementation (NON-NEGOTIABLE)
Claude Code must be the primary implementer of all code changes; All changes must be traceable through Prompt History Records; Implementation must follow the defined architectural patterns; Manual code changes must be reviewed against the constitution.

### XXI. Test-First Development (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced; Both unit and integration tests required for all features; AI behavior must be tested with realistic scenarios.

## Governance

Constitution supersedes all other practices; Amendments require documentation, approval, and migration plan; All PRs/reviews must verify compliance; Complexity must be justified; Use project documentation for runtime development guidance; All architectural decisions affecting the core principles must be documented in ADRs.

## Amendment Procedure

Changes to this constitution require:
1. Formal proposal with justification
2. Technical review by senior team members
3. Testing of proposed changes in a staging environment
4. Approval by project stakeholders
5. Migration plan for existing codebase
6. Update to all dependent templates and documentation