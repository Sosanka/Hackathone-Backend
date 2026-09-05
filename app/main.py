from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.router import router as v1_router


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",

        # ADD YOUR FRONTEND VERCEL URL HERE
        # "https://your-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = Path("uploads/products")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(v1_router)


# ============================================================
# FAVICON
# ============================================================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "Welcome to Hackathone API",
        "version": settings.APP_VERSION,
    }