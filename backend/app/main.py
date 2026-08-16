from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from backend.app.api.ai import router as ai_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.auth import router as auth_router
from backend.app.api.brain import router as brain_router
from backend.app.api.candidates import router as candidates_router
from backend.app.api.logs import router as logs_router
from backend.app.api.research import router as research_router
from backend.app.api.settings import router as settings_router
from backend.app.api.simulations import router as simulations_router
from backend.app.config import settings
from backend.app.core.exceptions import VerdeException
from backend.app.core.logging import verde_logger
from backend.app.database.models import FamilyPerformance, FieldPerformance, OperatorPerformance, ResearchFamily
from backend.app.database.session import AsyncSessionFactory, init_db
from backend.app.generation.family_info import RESEARCH_FAMILIES
from backend.app.generation.field_registry import FIELD_REGISTRY
from backend.app.generation.operator_registry import OPERATOR_REGISTRY
from backend.app.workers.worker import research_worker


async def seed_initial_registries():
    """Populates relational tables with default research families, fields, and operators."""
    async with AsyncSessionFactory() as session:
        # Seed Families
        for code, data in RESEARCH_FAMILIES.items():
            stmt = select(FamilyPerformance).where(FamilyPerformance.family_code == code)
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                session.add(FamilyPerformance(family_code=code))

        # Seed Fields
        for name in FIELD_REGISTRY.keys():
            stmt = select(FieldPerformance).where(FieldPerformance.field_name == name)
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                session.add(FieldPerformance(field_name=name))

        # Seed Operators
        for name in OPERATOR_REGISTRY.keys():
            stmt = select(OperatorPerformance).where(OperatorPerformance.operator_name == name)
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                session.add(OperatorPerformance(operator_name=name))

        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    verde_logger.log_event(
        event="SERVER_START",
        component="SYSTEM",
        message="VERDE Quant Research Platform starting up..."
    )
    await init_db()
    await seed_initial_registries()
    verde_logger.log_event(
        event="DATABASE_CONNECTED",
        component="DATABASE",
        message="Database tables initialized and initial registries seeded."
    )
    # Reconcile orphaned running simulations on startup
    try:
        from backend.app.brain.simulation import simulation_orchestrator
        async with AsyncSessionFactory() as session:
            reconciled = await simulation_orchestrator.reconcile_running_simulations(session)
            verde_logger.log_event(
                event="RECONCILE_ON_STARTUP",
                component="SYSTEM",
                message=f"Startup simulation reconciliation complete: {reconciled} running simulations resolved."
            )
    except Exception as e:
        verde_logger.log_event(
            event="RECONCILE_STARTUP_ERROR",
            severity="WARNING",
            component="SYSTEM",
            message=f"Error in startup simulation reconciliation: {str(e)}"
        )
    await research_worker.start()
    yield
    # Shutdown
    await research_worker.stop()
    verde_logger.log_event(
        event="SERVER_SHUTDOWN",
        component="SYSTEM",
        message="VERDE server shutting down."
    )


app = FastAPI(
    title="VERDE",
    description="Validation, Exploration & Research-driven Discovery Engine for WorldQuant BRAIN",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(brain_router)
app.include_router(candidates_router)
app.include_router(simulations_router)
app.include_router(analytics_router)
app.include_router(research_router)
app.include_router(ai_router)
app.include_router(settings_router)
app.include_router(logs_router)


# Global Exception Handler
@app.exception_handler(VerdeException)
async def verde_exception_handler(request: Request, exc: VerdeException):
    verde_logger.log_event(
        event="EXCEPTION_HANDLED",
        severity="WARNING",
        component="API",
        message=f"{exc.code}: {exc.message}",
        metadata=exc.details
    )
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


# Health endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "CONNECTED"
    }


# Static Frontend mount
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))
