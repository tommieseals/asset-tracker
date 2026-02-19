"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .config import settings
from .database import engine, Base
from .routers import users, assets, audit, search, qr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Asset Inventory Tracker",
    description="Internal portal for tracking company assets",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(qr.router, prefix="/api/qr", tags=["qr"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
