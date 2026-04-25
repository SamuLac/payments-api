"""
Payments API - Entry point

A simplified payment processing API built with FastAPI.
Supports creating payments, uploading receipts to AWS S3,
and querying payment history.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import payments, receipts
from app.database import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Roda ao iniciar a aplicação
    Base.metadata.create_all(bind=engine)
    yield
    # Roda ao encerrar (cleanup se necessário)

app = FastAPI(
    title="Payments API",
    lifespan=lifespan,
    description="""
## Payments API

A simplified payment processing system with AWS S3 receipt storage.

### Features
- Create and manage payments
- Upload receipts directly to AWS S3
- Query payment history with filters
- Full OpenAPI documentation
    """,
    version="1.0.0",
    contact={
        "name": "Samuel Lacerda",
        "url": "https://github.com/SamuLac",
        "email": "samuel.lacerdaif@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint. Returns API status."""
    return {"status": "ok", "service": "payments-api", "version": "1.0.0"}
