# SpecKit Plus Templates

## API Service Template

For REST/GraphQL API services.

### Structure
```
api-service/
├── .speckit/
│   ├── constitution.md
│   └── specifications/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── schemas/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   ├── services/
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── requirements.txt
└── Dockerfile
```

### Constitution Template
```markdown
# API Service Constitution

## Technical Stack
- Framework: FastAPI
- Database: PostgreSQL with SQLAlchemy
- Authentication: JWT
- Documentation: OpenAPI/Swagger

## Standards
- RESTful design principles
- Semantic versioning for API
- Request/response validation with Pydantic
- Structured logging (JSON format)
```

---

## Multi-Agent System Template

For OpenAI Agents SDK applications.

### Structure
```
multi-agent/
├── .speckit/
│   ├── constitution.md
│   └── specifications/
│       ├── agents/
│       └── workflows/
├── src/
│   ├── agents/
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   └── specialists/
│   ├── tools/
│   ├── protocols/
│   └── main.py
├── tests/
└── requirements.txt
```

### Agent Specification Template
```markdown
# Agent: [Name]

## Role
[Agent's purpose and responsibilities]

## Capabilities
- [Capability 1]
- [Capability 2]

## Tools
| Tool | Purpose |
|------|---------|
| tool_name | description |

## Communication
- **Receives from:** [agents]
- **Sends to:** [agents]
- **Protocol:** [A2A/MCP]

## Constraints
- [Limitation 1]
- [Limitation 2]
```

---

## Kubernetes Deployment Template

For containerized applications.

### Structure
```
k8s-deployment/
├── .speckit/
│   ├── constitution.md
│   └── specifications/
│       └── infrastructure/
├── src/
├── k8s/
│   ├── base/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── overlays/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── kustomization.yaml
├── Dockerfile
└── skaffold.yaml
```

### Infrastructure Spec Template
```markdown
# Infrastructure Specification

## Compute
- CPU: [requests/limits]
- Memory: [requests/limits]
- Replicas: [min/max]

## Networking
- Service type: [ClusterIP/LoadBalancer]
- Ingress: [yes/no]
- TLS: [requirements]

## Storage
- Persistent volumes: [requirements]
- Storage class: [type]

## Scaling
- HPA targets: [metrics]
- Scale triggers: [conditions]
```

---

## Dapr Application Template

For distributed applications using Dapr runtime.

### Structure
```
dapr-app/
├── .speckit/
│   ├── constitution.md
│   └── specifications/
├── src/
│   ├── services/
│   └── components/
├── dapr/
│   ├── components/
│   │   ├── pubsub.yaml
│   │   ├── statestore.yaml
│   │   └── secrets.yaml
│   └── config.yaml
└── docker-compose.yaml
```

### Dapr Component Spec Template
```markdown
# Dapr Component: [Name]

## Type
[pubsub/statestore/binding/secretstore]

## Provider
[Redis/Kafka/PostgreSQL/etc.]

## Configuration
| Key | Value | Description |
|-----|-------|-------------|
| ... | ... | ... |

## Usage
- Services using: [list]
- Operations: [publish/subscribe/get/set]
```

---

## Specification Templates

### User Story Template
```markdown
### US-[ID]: [Title]

**As a** [user role]
**I want** [goal/desire]
**So that** [benefit/value]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

**Technical Notes:**
- [Implementation hints]

**Dependencies:**
- [Related stories/tasks]
```

### API Endpoint Template
```markdown
### [METHOD] /api/v1/[resource]

**Purpose:** [description]

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
| 400 | Invalid input |
| 401 | Unauthorized |
| 404 | Not found |

**Authorization:** [requirements]
```

### Data Model Template
```markdown
## Entity: [Name]

**Purpose:** [description]

**Fields:**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| ... | ... | ... | ... |

**Relationships:**
- [Entity] → [Related Entity]: [type]

**Indexes:**
- [field(s)] - [purpose]

**Constraints:**
- [Business rules]
```
