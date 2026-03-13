# Learning Center FastAPI Backend

This is the FastAPI-based backend for the Learning Center project, featuring:
- **Authentication**: JWT-based security with password hashing.
- **RBAC**: Role-Based Access Control (Admin, Teacher, Student, Parent).
- **ORM**: SQLAlchemy with PostgreSQL support.
- **Package Management**: Managed with `uv`.

## GitHub Repository
[https://github.com/Ishowar84/learningcenter_fastapi_backend.git](https://github.com/Ishowar84/learningcenter_fastapi_backend.git)

## Getting Started

### Prerequisites
- Python 3.10+
- `uv` installed (`pip install uv`)

### Running Locally
1. Sync dependencies:
   ```bash
   uv sync
   ```
2. Run development server:
   ```bash
   make dev
   ```

## API Documentation
Once running, visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the Swagger UI.
