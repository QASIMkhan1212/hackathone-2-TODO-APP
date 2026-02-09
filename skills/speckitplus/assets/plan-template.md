# Technical Plan: {{FEATURE_NAME}}

**Version:** 1.0
**Status:** Draft | In Review | Approved
**Author:** {{AUTHOR}}
**Date:** {{DATE}}
**Specification:** {{SPEC_REFERENCE}}

---

## Architecture Overview

{{HIGH_LEVEL_ARCHITECTURE_DESCRIPTION}}

```
┌─────────────────┐     ┌─────────────────┐
│   {{COMPONENT}}  │────▶│   {{COMPONENT}}  │
└─────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   {{COMPONENT}}  │     │   {{COMPONENT}}  │
└─────────────────┘     └─────────────────┘
```

---

## Component Design

### Component 1: {{COMPONENT_NAME}}

**Purpose:** {{DESCRIPTION}}

**Responsibilities:**
- {{RESPONSIBILITY_1}}
- {{RESPONSIBILITY_2}}

**Interfaces:**
```typescript
interface {{InterfaceName}} {
  {{method}}({{params}}): {{ReturnType}};
}
```

**Dependencies:**
- {{DEPENDENCY}}: {{REASON}}

---

### Component 2: {{COMPONENT_NAME}}

**Purpose:** {{DESCRIPTION}}

**Responsibilities:**
- {{RESPONSIBILITY_1}}
- {{RESPONSIBILITY_2}}

---

## Data Model

### Schema Changes

```sql
-- New table
CREATE TABLE {{table_name}} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    {{column}} {{TYPE}} {{CONSTRAINTS}},
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_{{table}}_{{column}} ON {{table}}({{column}});
```

### Migrations
1. `001_create_{{table}}.sql`: Create initial table
2. `002_add_{{feature}}.sql`: Add new columns

---

## API Design

### Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/v1/{{resource}} | List all |
| POST | /api/v1/{{resource}} | Create new |
| GET | /api/v1/{{resource}}/:id | Get single |
| PUT | /api/v1/{{resource}}/:id | Update |
| DELETE | /api/v1/{{resource}}/:id | Delete |

### Request/Response Schemas

See [API Specification](./api-spec.md) for detailed schemas.

---

## Implementation Approach

### Phase 1: Foundation ({{DURATION}})
1. {{TASK_1}}
2. {{TASK_2}}
3. {{TASK_3}}

### Phase 2: Core Features ({{DURATION}})
1. {{TASK_1}}
2. {{TASK_2}}

### Phase 3: Integration ({{DURATION}})
1. {{TASK_1}}
2. {{TASK_2}}

### Phase 4: Polish ({{DURATION}})
1. {{TASK_1}}
2. {{TASK_2}}

---

## Testing Strategy

### Unit Tests
- Coverage target: >80%
- Focus areas: {{AREAS}}

### Integration Tests
- API endpoint testing
- Database integration
- External service mocking

### E2E Tests
- Critical user flows
- Cross-browser testing

### Performance Tests
- Load testing: {{SCENARIO}}
- Stress testing: {{SCENARIO}}

---

## Security Considerations

### Authentication
{{AUTH_APPROACH}}

### Authorization
{{AUTHZ_APPROACH}}

### Data Protection
- [ ] Sensitive data encrypted
- [ ] PII handling compliant
- [ ] Audit logging enabled

### Input Validation
- [ ] All inputs validated
- [ ] SQL injection prevented
- [ ] XSS prevented

---

## Performance Considerations

### Caching Strategy
- {{CACHE_APPROACH}}

### Database Optimization
- Indexes: {{INDEXES}}
- Query optimization: {{APPROACH}}

### Scalability
- {{SCALABILITY_APPROACH}}

---

## Monitoring & Observability

### Metrics
- {{METRIC_1}}: {{DESCRIPTION}}
- {{METRIC_2}}: {{DESCRIPTION}}

### Logging
- Log level: {{LEVEL}}
- Structured logging format

### Alerts
- {{ALERT_CONDITION}}: {{ACTION}}

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| {{RISK_1}} | High | Medium | {{MITIGATION}} |
| {{RISK_2}} | Medium | Low | {{MITIGATION}} |

---

## Dependencies & Blockers

### Dependencies
- [ ] {{DEPENDENCY_1}}: {{STATUS}}
- [ ] {{DEPENDENCY_2}}: {{STATUS}}

### Blockers
- {{BLOCKER}}: {{RESOLUTION_PLAN}}

---

## Rollback Plan

1. {{ROLLBACK_STEP_1}}
2. {{ROLLBACK_STEP_2}}
3. {{ROLLBACK_STEP_3}}

---

## Open Questions

- [ ] {{QUESTION_1}}
- [ ] {{QUESTION_2}}

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{DATE}} | {{AUTHOR}} | Initial plan |
