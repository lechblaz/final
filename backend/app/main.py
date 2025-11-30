"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="Personal Finance Manager API",
    description="API for managing personal finances with flat tag system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Personal Finance Manager API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Import routers
from app.api.v1 import transactions, imports, merchants

app.include_router(transactions.router, prefix="/api/v1", tags=["transactions"])
app.include_router(imports.router, prefix="/api/v1", tags=["imports"])
app.include_router(merchants.router, prefix="/api/v1", tags=["merchants"])

# TODO: Add these routers as they are implemented
# from app.api.v1 import tags
# app.include_router(tags.router, prefix="/api/v1", tags=["tags"])
