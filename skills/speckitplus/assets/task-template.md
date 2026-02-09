# Tasks: {{FEATURE_NAME}}

**Generated:** {{DATE}}
**Plan Reference:** {{PLAN_REFERENCE}}
**Specification:** {{SPEC_REFERENCE}}

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | {{COUNT}} |
| High Priority | {{COUNT}} |
| Medium Priority | {{COUNT}} |
| Low Priority | {{COUNT}} |

---

## Phase 1: {{PHASE_NAME}}

### TASK-001: {{TASK_TITLE}}

**Priority:** High | Medium | Low
**Estimate:** {{ESTIMATE}}
**Assignee:** {{ASSIGNEE}}
**Status:** Pending | In Progress | Blocked | Done

**Description:**
{{DETAILED_DESCRIPTION}}

**Dependencies:**
- {{DEPENDENCY}}

**Acceptance Criteria:**
- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}
- [ ] {{CRITERION_3}}

**Technical Notes:**
- {{NOTE_1}}
- {{NOTE_2}}

---

### TASK-002: {{TASK_TITLE}}

**Priority:** High | Medium | Low
**Estimate:** {{ESTIMATE}}
**Assignee:** {{ASSIGNEE}}
**Status:** Pending | In Progress | Blocked | Done

**Description:**
{{DETAILED_DESCRIPTION}}

**Dependencies:**
- TASK-001

**Acceptance Criteria:**
- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}

---

## Phase 2: {{PHASE_NAME}}

### TASK-003: {{TASK_TITLE}}

**Priority:** High | Medium | Low
**Estimate:** {{ESTIMATE}}
**Assignee:** {{ASSIGNEE}}
**Status:** Pending | In Progress | Blocked | Done

**Description:**
{{DETAILED_DESCRIPTION}}

**Dependencies:**
- TASK-001
- TASK-002

**Acceptance Criteria:**
- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}

---

## Testing Tasks

### TASK-T01: Write Unit Tests

**Priority:** High
**Estimate:** {{ESTIMATE}}
**Status:** Pending

**Scope:**
- [ ] {{COMPONENT_1}} tests
- [ ] {{COMPONENT_2}} tests

**Coverage Target:** >80%

---

### TASK-T02: Write Integration Tests

**Priority:** Medium
**Estimate:** {{ESTIMATE}}
**Status:** Pending

**Scope:**
- [ ] API endpoint tests
- [ ] Database integration tests

---

## Documentation Tasks

### TASK-D01: Update API Documentation

**Priority:** Low
**Estimate:** {{ESTIMATE}}
**Status:** Pending

**Scope:**
- [ ] OpenAPI spec updated
- [ ] README updated
- [ ] Examples added

---

## Deployment Tasks

### TASK-DEP01: Prepare Deployment

**Priority:** High
**Estimate:** {{ESTIMATE}}
**Status:** Pending

**Checklist:**
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Rollback plan documented
- [ ] Monitoring dashboards updated

---

## Task Dependencies Graph

```
TASK-001 ─────┬────▶ TASK-003 ────▶ TASK-T01
              │
TASK-002 ─────┘                      │
                                     ▼
                              TASK-DEP01
```

---

## Blocked Tasks

| Task | Blocker | Resolution | ETA |
|------|---------|------------|-----|
| {{TASK}} | {{BLOCKER}} | {{RESOLUTION}} | {{DATE}} |

---

## Completed Tasks

| Task | Completed | Notes |
|------|-----------|-------|
| - | - | - |

---

## Notes

- {{NOTE_1}}
- {{NOTE_2}}
