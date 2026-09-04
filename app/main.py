from fastapi import FastAPI

from app.core.config import settings
from app.v1.router import router as v1_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


app.include_router(v1_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Hackathone API",
        "version": settings.APP_VERSION,
    }