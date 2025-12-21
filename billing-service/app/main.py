import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.consul_client import consul_client
from app.routers import bills
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting Billing Service...")
    create_db_and_tables()
    consul_client.register_service()
    yield
    # Shutdown
    print("🛑 Shutting down Billing Service...")
    consul_client.deregister_service()


app = FastAPI(
    title="Billing Service",
    description="Microservice for managing bills and invoices",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
# Note: bills.router usually has prefix="/bills", so this makes it /api/bills
app.include_router(bills.router, prefix="/api")


@app.get("/health")
def health_check():
    """Health check endpoint for Consul"""
    return {"status": "healthy", "service": settings.service_name}


@app.get("/")
def root():
    """Root endpoint"""
    return {"service": settings.service_name, "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, reload=True)
