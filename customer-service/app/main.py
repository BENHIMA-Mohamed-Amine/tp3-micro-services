import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.consul_client import consul_client
from app.routers import customers
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting Customer Service...")
    create_db_and_tables()
    consul_client.register_service()
    yield
    # Shutdown
    print("🛑 Shutting down Customer Service...")
    consul_client.deregister_service()


app = FastAPI(
    title="Customer Service",
    description="Microservice for managing customers",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(customers.router, prefix="/api")


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