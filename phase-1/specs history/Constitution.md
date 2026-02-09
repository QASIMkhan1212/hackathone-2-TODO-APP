1→/sp.constitution
     2→
     3→Project: Todo In-Memory Python API Application
     4→
     5→Core principles:
     6→- Spec-driven development using Claude Code and Spec-Kit Plus
     7→- Clean code principles with proper Python project structure
     8→- Agentic Dev Stack workflow (spec → plan → tasks → implement)
     9→- Memory-based storage for simplicity and performance
    10→- Comprehensive error handling and user experience
    11→
    12→Key standards:
    13→- Python 3.13+ with modern Python features
    14→- UV for package and dependency management
    15→- Type hints for all public interfaces
    16→- Docstrings following Google style
    17→- Error handling with custom exceptions where appropriate
    18→- Logging for debugging and audit purposes
    19→- Test-driven development with pytest
    20→
    21→Constraints:
    22→- No database or file persistence (memory-only)
    23→- REST API using FastAPI (no GUI)
    24→- Single file implementation for core logic
    25→- Maximum 50 lines per function for readability
    26→- Strict adherence to PEP 8 style guidelines
    27→- Zero external dependencies except standard library + pytest
    28→
    29→Success criteria:
    30→- All 5 basic features fully implemented (Add, Delete, Update, View, Mark Complete)
    31→- Clean, maintainable code following Python best practices
    32→- Comprehensive error handling and user feedback
    33→- Full test coverage with pytest
    34→- Professional project structure with proper documentation
    35→- Working API Endpoints
    36→
    37→Technical requirements:
    38→- Task data structure with title, description, status, and ID
    39→- API endpoints with clear routes
    40→- Input validation and sanitization
    41→- Proper separation of concerns (business logic vs API endpoints)
    42→- Memory-efficient task storage with O(1) operations
