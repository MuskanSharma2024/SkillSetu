from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.config import settings
from app.database import engine, Base
from app.seed import seed_database
from app.routers import (
    auth, students, companies, institutions, documents, dashboards, skills, opportunities, portfolio, analytics
)

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SkillSetu: Bridging Academia and Industry through Skill Assessment, Opportunity Matching, and Curriculum Feedback Loops.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for seamless development/testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(students.router, prefix=settings.API_V1_STR)
app.include_router(companies.router, prefix=settings.API_V1_STR)
app.include_router(institutions.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(dashboards.router, prefix=settings.API_V1_STR)
app.include_router(skills.router, prefix=settings.API_V1_STR)
app.include_router(opportunities.router, prefix=settings.API_V1_STR)
app.include_router(portfolio.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "database": "connected"
    }

# Frontend static serving
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

@app.on_event("startup")
def on_startup():
    """Create database tables and seed baseline demo records on application start."""
    Base.metadata.create_all(bind=engine)
    seed_database()

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    @app.get("/index.html", include_in_schema=False)
    def serve_frontend_root():
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "SkillSetu API is running. Frontend index.html not yet created."}

    @app.get("/dashboards/{dashboard_name}.html", include_in_schema=False)
    @app.get("/dashboards/{dashboard_name}", include_in_schema=False)
    def serve_dashboard_page(dashboard_name: str):
        dash_name = dashboard_name if dashboard_name.endswith(".html") else f"{dashboard_name}.html"
        dash_path = FRONTEND_DIR / "dashboards" / dash_name
        if dash_path.exists():
            return FileResponse(str(dash_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))

