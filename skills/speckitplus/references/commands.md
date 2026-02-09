# SpecKit Plus Commands Reference

## /sp.constitution

Establish project governing principles and constraints.

**Usage:**
```
/sp.constitution
```

**Creates:** `.speckit/constitution.md`

**Content includes:**
- Project mission and goals
- Technical constraints (languages, frameworks)
- Quality standards
- Security requirements
- Performance targets
- Team conventions

**Example output structure:**
```markdown
# Project Constitution

## Mission
[Project purpose and goals]

## Technical Stack
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL
- Deployment: Kubernetes

## Quality Standards
- Test coverage: >80%
- Documentation: Required for public APIs
- Code review: Required before merge

## Security Requirements
- Authentication: JWT tokens
- Authorization: Role-based access control
- Data encryption: At rest and in transit
```

---

## /sp.specify

Define requirements, user stories, and acceptance criteria.

**Usage:**
```
/sp.specify [feature-name]
```

**Creates:** `.speckit/specifications/<feature-name>.md`

**Specification structure:**
```markdown
# Feature: [Name]

## Overview
[Brief description]

## User Stories

### US-001: [Story Title]
**As a** [user type]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

## Non-Functional Requirements
- Performance: [targets]
- Security: [requirements]
- Scalability: [expectations]

## Dependencies
- [List of dependencies]

## Open Questions
- [Unresolved items for /sp.clarify]
```

---

## /sp.plan

Create technical implementation strategy from specifications.

**Usage:**
```
/sp.plan [specification-file]
```

**Creates:** `.speckit/plans/<plan-name>.md`

**Plan structure:**
```markdown
# Technical Plan: [Feature]

## Architecture Overview
[High-level design]

## Component Design

### Component 1
- Purpose: [description]
- Interfaces: [APIs/contracts]
- Dependencies: [requirements]

## Data Model
[Schema definitions]

## API Design
[Endpoint specifications]

## Implementation Approach
1. Phase 1: [description]
2. Phase 2: [description]

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| ... | ... | ... |

## Testing Strategy
- Unit tests: [approach]
- Integration tests: [approach]
- E2E tests: [approach]
```

---

## /sp.tasks

Generate actionable task lists from plans.

**Usage:**
```
/sp.tasks [plan-file]
```

**Creates:** `.speckit/tasks/<task-list>.md`

**Task format:**
```markdown
# Tasks: [Feature]

## Phase 1: Foundation

### TASK-001: [Title]
- **Priority:** High/Medium/Low
- **Estimate:** [time]
- **Dependencies:** [task IDs]
- **Description:** [details]
- **Acceptance:** [criteria]

### TASK-002: [Title]
...

## Phase 2: Implementation
...
```

---

## /sp.implement

Execute tasks following the implementation plan.

**Usage:**
```
/sp.implement [task-id]
```

**Workflow:**
1. Read task specification
2. Check dependencies are complete
3. Implement following plan guidelines
4. Run tests
5. Update task status
6. Document any deviations

---

## /sp.clarify

Resolve ambiguities and underspecified areas.

**Usage:**
```
/sp.clarify [specification-file]
```

**Actions:**
- Identifies unclear requirements
- Generates clarifying questions
- Documents assumptions
- Updates specifications with answers

---

## /sp.analyze

Cross-artifact consistency validation.

**Usage:**
```
/sp.analyze
```

**Checks:**
- Specification completeness
- Plan-to-spec alignment
- Task coverage
- Dependency consistency
- Test coverage mapping

**Output:** Analysis report with issues and recommendations

---

## /sp.checklist

Generate quality validation checklists.

**Usage:**
```
/sp.checklist [phase]
```

**Phases:**
- `pre-implementation`: Before coding
- `pre-review`: Before code review
- `pre-release`: Before deployment

**Example checklist:**
```markdown
# Pre-Release Checklist

## Code Quality
- [ ] All tests passing
- [ ] Code coverage meets threshold
- [ ] No critical linting errors
- [ ] Documentation updated

## Security
- [ ] Security scan completed
- [ ] No exposed secrets
- [ ] Authentication verified

## Performance
- [ ] Load tests passed
- [ ] Response times within SLA
- [ ] Resource utilization acceptable
```
