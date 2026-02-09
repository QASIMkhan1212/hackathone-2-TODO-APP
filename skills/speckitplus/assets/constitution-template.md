# Project Constitution: {{PROJECT_NAME}}

Created: {{DATE}}
Version: 1.0

## Mission

{{PROJECT_MISSION}}

## Goals

1. {{GOAL_1}}
2. {{GOAL_2}}
3. {{GOAL_3}}

## Technical Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Language** | {{LANGUAGE}} | {{VERSION}} |
| **Framework** | {{FRAMEWORK}} | {{VERSION}} |
| **Database** | {{DATABASE}} | {{VERSION}} |
| **Cache** | {{CACHE}} | {{VERSION}} |
| **Deployment** | {{DEPLOYMENT}} | - |

## Architecture Principles

1. **Separation of Concerns**: Keep business logic, data access, and presentation layers distinct
2. **DRY (Don't Repeat Yourself)**: Extract common patterns into reusable components
3. **SOLID Principles**: Follow single responsibility, open-closed, and dependency inversion
4. **Fail Fast**: Validate inputs early and provide clear error messages

## Quality Standards

### Code Quality
- Test coverage: >80%
- All public functions documented
- No critical linting errors
- Code review required before merge

### Performance Targets
- API response time: <200ms (p95)
- Page load time: <3s
- Uptime: 99.9%

### Security Requirements
- [ ] Authentication: {{AUTH_METHOD}}
- [ ] Authorization: {{AUTHZ_MODEL}}
- [ ] Data encryption at rest
- [ ] TLS for all connections
- [ ] Input validation on all endpoints
- [ ] Rate limiting enabled

## Development Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `fix/*`: Bug fixes
- `release/*`: Release preparation

### Commit Convention
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Review Process
1. Create PR with description
2. Automated tests must pass
3. At least 1 approval required
4. Squash merge to main

## Constraints

### Must Have
- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}

### Must NOT Have
- {{ANTI_CONSTRAINT_1}}
- {{ANTI_CONSTRAINT_2}}

## Dependencies

### External Services
- {{SERVICE_1}}: {{PURPOSE}}
- {{SERVICE_2}}: {{PURPOSE}}

### Third-Party Libraries
- Prefer well-maintained, actively developed libraries
- Security audit required for new dependencies
- License must be compatible with project

## Glossary

| Term | Definition |
|------|------------|
| {{TERM_1}} | {{DEFINITION_1}} |
| {{TERM_2}} | {{DEFINITION_2}} |
