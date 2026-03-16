# Learning Center FastAPI Backend

This is the FastAPI-based backend for the Learning Center project, featuring:
- **Authentication**: JWT-based security with password hashing (Bcrypt).
- **RBAC**: Role-Based Access Control (Admin, Teacher, Student, Parent, Partner Admin).
- **Enrollment Workflow**: Complete request/approval system for course enrollments.
- **ORM**: SQLAlchemy with cross-model relationships and eager loading.
- **Migrations**: Database schema versioning with Alembic.
- **Data Schemas**: Pydantic models with `CamelModel` for seamless frontend integration.

## Core Features
- ✅ **Course Management**: CRUD operations for courses and subjects.
- ✅ **User Management**: Unified profile updates and administrative user controls.
- ✅ **Enrollment Process**: Integrated student request and multi-level approval (Parent/Admin).
- ✅ **Exception Handling**: Global error normalization for consistent frontend error handling.

## Getting Started

### Prerequisites
- Python 3.10+
- `uv` installed (`pip install uv`)

### Running Locally
1. Sync dependencies:
   ```bash
   uv sync
   ```
2. Apply migrations:
   ```bash
   uv run alembic upgrade head
   ```
3. Run development server:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

## API Documentation
Once running, visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the Swagger UI.

