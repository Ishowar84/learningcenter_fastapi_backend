import socket
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1 import auth_router, admin_router, courses_router, users_router, enrollments_router, assignments_router, submissions_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    hostname = socket.gethostname()
    local_ip = "127.0.0.1"
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        pass

    print("\n" + "="*50)
    print(f"🚀 {settings.PROJECT_NAME} is running!")
    print(f"➜  Local:   http://127.0.0.1:8000/docs")
    print(f"➜  Network: http://{local_ip}:8000/docs")
    print("="*50 + "\n")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
async def root():
    return {"message": "Welcome to Learning Center API", "docs": "/docs"}

@app.get("/uptime", tags=["uptime"])
async def uptime_check(request: Request):
    """
    Public uptime endpoint — no authentication required.
    Logs each ping (timestamp only) to the database.
    Cleans up entries older than 24 hours to keep the table lean.
    Intended for use with Uptime Robot to keep Render free tier alive.
    """
    from app.db.session import SessionLocal
    from app.models.health_check import UptimeLog

    db = SessionLocal()
    error_detail = None
    try:
        # Insert a new ping log
        log = UptimeLog()
        db.add(log)

        # Delete entries older than 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        db.query(UptimeLog).filter(UptimeLog.called_at < cutoff).delete()

        db.commit()

        # Count pings in last 24 hours
        recent_count = db.query(UptimeLog).count()
    except Exception as e:
        db.rollback()
        error_detail = str(e)
        print(f"❌ Uptime log failed: {error_detail}")
        recent_count = -1
    finally:
        db.close()

    return {
        "status": "ok" if recent_count != -1 else "error",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pings_last_24h": recent_count,
        "detail": error_detail
    }

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = "; ".join([f"{'.'.join([str(loc) for loc in err['loc']])}: {err['msg']}" for err in errors])
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": f"Validation error: {error_msg}"}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc) or "Internal server error"}
    )


# Include routers
app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(admin_router.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(courses_router.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(users_router.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(users_router.router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["admin-users"])
app.include_router(enrollments_router.router, prefix=f"{settings.API_V1_STR}/enrollments", tags=["enrollments"])
app.include_router(assignments_router.router, prefix=f"{settings.API_V1_STR}/assignments", tags=["assignments"])
app.include_router(submissions_router.router, prefix=f"{settings.API_V1_STR}/submissions", tags=["submissions"])
