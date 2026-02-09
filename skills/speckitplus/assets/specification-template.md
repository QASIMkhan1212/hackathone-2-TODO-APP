# Feature Specification: {{FEATURE_NAME}}

**Version:** 1.0
**Status:** Draft | In Review | Approved
**Author:** {{AUTHOR}}
**Date:** {{DATE}}

---

## Overview

{{BRIEF_DESCRIPTION}}

### Problem Statement

{{PROBLEM_BEING_SOLVED}}

### Proposed Solution

{{HIGH_LEVEL_SOLUTION}}

---

## User Stories

### US-001: {{STORY_TITLE}}

**As a** {{USER_ROLE}}
**I want** {{CAPABILITY}}
**So that** {{BENEFIT}}

**Acceptance Criteria:**
- [ ] Given {{CONTEXT}}, when {{ACTION}}, then {{OUTCOME}}
- [ ] Given {{CONTEXT}}, when {{ACTION}}, then {{OUTCOME}}
- [ ] Given {{CONTEXT}}, when {{ACTION}}, then {{OUTCOME}}

**Priority:** High | Medium | Low
**Estimate:** {{STORY_POINTS}}

---

### US-002: {{STORY_TITLE}}

**As a** {{USER_ROLE}}
**I want** {{CAPABILITY}}
**So that** {{BENEFIT}}

**Acceptance Criteria:**
- [ ] Given {{CONTEXT}}, when {{ACTION}}, then {{OUTCOME}}
- [ ] Given {{CONTEXT}}, when {{ACTION}}, then {{OUTCOME}}

**Priority:** High | Medium | Low
**Estimate:** {{STORY_POINTS}}

---

## Functional Requirements

### FR-001: {{REQUIREMENT_TITLE}}
{{REQUIREMENT_DESCRIPTION}}

### FR-002: {{REQUIREMENT_TITLE}}
{{REQUIREMENT_DESCRIPTION}}

---

## Non-Functional Requirements

### Performance
- Response time: {{TARGET}}
- Throughput: {{TARGET}}
- Concurrent users: {{TARGET}}

### Security
- Authentication: {{REQUIREMENT}}
- Authorization: {{REQUIREMENT}}
- Data protection: {{REQUIREMENT}}

### Scalability
- {{SCALABILITY_REQUIREMENT}}

### Availability
- Uptime target: {{TARGET}}
- Recovery time objective: {{TARGET}}

---

## Data Model

### Entities

#### {{ENTITY_NAME}}
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| {{FIELD}} | {{TYPE}} | {{CONSTRAINTS}} | {{DESCRIPTION}} |

### Relationships
- {{ENTITY_A}} → {{ENTITY_B}}: {{RELATIONSHIP_TYPE}}

---

## API Design

### {{METHOD}} /api/v1/{{RESOURCE}}

**Purpose:** {{DESCRIPTION}}

**Request:**
```json
{
  "field": "type - description"
}
```

**Response (200):**
```json
{
  "field": "type - description"
}
```

**Errors:**
| Code | Condition |
|------|-----------|
| 400 | {{CONDITION}} |
| 401 | {{CONDITION}} |
| 404 | {{CONDITION}} |

---

## UI/UX Requirements

### Screens
1. {{SCREEN_NAME}}: {{DESCRIPTION}}
2. {{SCREEN_NAME}}: {{DESCRIPTION}}

### User Flows
1. {{FLOW_DESCRIPTION}}

---

## Dependencies

### Internal
- {{DEPENDENCY}}: {{REASON}}

### External
- {{SERVICE}}: {{REASON}}

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| {{RISK}} | High/Med/Low | High/Med/Low | {{MITIGATION}} |

---

## Open Questions

- [ ] {{QUESTION_1}}
- [ ] {{QUESTION_2}}

---

## Appendix

### References
- {{REFERENCE_1}}
- {{REFERENCE_2}}

### Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{DATE}} | {{AUTHOR}} | Initial draft |
