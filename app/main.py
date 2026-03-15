import socket
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth_router, admin_router, courses_router, users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Determine local network IP
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

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
async def root():
    return {"message": "Welcome to Learning Center API", "docs": "/docs"}

# Include routers
app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(admin_router.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(courses_router.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(users_router.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(users_router.router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["admin-users"])
