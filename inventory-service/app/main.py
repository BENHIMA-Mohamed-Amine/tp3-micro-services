import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import products
from .consul_client import consul_client
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    consul_client.register_service()
    yield
    consul_client.deregister_service()


app = FastAPI(title="Inventory Service", lifespan=lifespan)
app.include_router(products.router)

@app.get("/")
def root():
    """Root endpoint"""
    return {"service": settings.service_name, "version": "1.0.0", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, reload=True)