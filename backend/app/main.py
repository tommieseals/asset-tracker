" Asset Inventory Tracker - FastAPI Backend Production-ready with JWT auth, RBAC, and AI search "
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import assets, users, audit, search, qr
from .config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    "Initialize database on startup"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(Database tables created)
    yield
    logger.info(Shutting down)

app = FastAPI(
    title=Asset Inventory Tracker,
    description=Internal portal for tracking company assets with AI-powered search,
    version=1.0.0,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=[*],
    allow_headers=[*],
)

# Include routers
app.include_router(users.router, prefix=/api/users, tags=[users])
app.include_router(assets.router, prefix=/api/assets, tags=[assets])
app.include_router(audit.router, prefix=/api/audit, tags=[audit])
app.include_router(search.router, prefix=/api/search, tags=[search])
app.include_router(qr.router, prefix=/api/qr, tags=[qr])

@app.get(/)
async def root():
    return {message: Asset Inventory Tracker API, version: 1.0.0}

@app.get(/health)
async def health():
    return {status: healthy}
EOF