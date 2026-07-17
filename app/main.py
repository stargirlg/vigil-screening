from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.logger import setup_logging
from app.api.routes import users, customers, screening, alerts, audit, dashboard
from app.api.routes import watchlist
from app.api.routes import cases
from app.api.routes import rules
from app.api.routes import reports
from app.api.routes import export

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Customer Screening & Compliance Engine for NBFC, Banks & BFSI",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(users.router)
app.include_router(customers.router)
app.include_router(screening.router)
app.include_router(alerts.router)
app.include_router(audit.router)
app.include_router(dashboard.router)
app.include_router(watchlist.router)
app.include_router(cases.router)
app.include_router(rules.router)
app.include_router(reports.router)
app.include_router(export.router)

@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}