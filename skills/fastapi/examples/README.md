# test-api

FastAPI project with best practices structure

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy .env.example to .env and update values:
```bash
cp .env.example .env
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

4. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
test-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   ├── core/
│   │   └── config.py
│   ├── models/
│   ├── schemas/
│   ├── crud/
│   └── main.py
└── tests/
```
