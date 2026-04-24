"""
Pydantic schemas

Defines the shape of data accepted and returned by the API.
FastAPI uses these for automatic validation and OpenAPI docs generation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.payment import PaymentStatus, PaymentMethod


class PaymentCreate(BaseModel):
    """Schema for creating a new payment."""

    description: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Short description of what is being paid",
        examples=["Monthly subscription - Plan Pro"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Amount in BRL (must be greater than 0)",
        examples=[149.90],
    )
    method: PaymentMethod = Field(
        ...,
        description="Payment method",
        examples=[PaymentMethod.PIX],
    )
    payer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the payer",
        examples=["Samuel Lacerda"],
    )
    payer_email: EmailStr = Field(
        ...,
        description="Payer email (used to send receipt)",
        examples=["samuel@email.com"],
    )

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v):
        """Ensures the amount is rounded to 2 decimal places."""
        return round(v, 2)


class PaymentUpdate(BaseModel):
    """Schema for updating a payment's status."""

    status: PaymentStatus = Field(
        ...,
        description="New status for the payment",
        examples=[PaymentStatus.COMPLETED],
    )


class PaymentResponse(BaseModel):
    """Schema for payment responses (what the API returns)."""

    id: UUID
    description: str
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    payer_name: str
    payer_email: str
    receipt_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    """Schema for paginated list of payments."""

    total: int
    page: int
    page_size: int
    results: list[PaymentResponse]
