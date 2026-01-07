from fastapi import FastAPI
from app.config import get_settings
from app.routers import urls

settings = get_settings()

app = FastAPI(
    title="URL Shortener API",
    description="A high-performance URL shortener with analytics",
    version="1.0.0",
)

app.include_router(urls.router)

@app.get("/")
async def root():
    return {"message": "URL Shortener API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}