from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="Agentic Backend API",
        description="Backend API for Agent-based application",
        version="0.1.0"
    )

    # Middleware for CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers here
    from src.api.routes import health
    app.include_router(health.router, prefix="/api/v1")

    return app
