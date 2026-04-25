"""
Payment model

Defines the 'payments' table schema using SQLAlchemy ORM.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    PIX = "pix"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BOLETO = "boleto"


class Payment(Base):
    """
    Represents a payment transaction.

    Attributes:
        id: Unique identifier (UUID v4)
        description: Human-readable description of the payment
        amount: Payment amount in BRL
        method: Payment method used (pix, credit_card, etc.)
        status: Current status of the payment
        payer_name: Full name of the person making the payment
        payer_email: Email of the payer (used for receipts)
        receipt_url: S3 URL of the uploaded receipt, if any
        created_at: Timestamp when payment was created
        updated_at: Timestamp of the last update
    """

    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payer_name = Column(String(100), nullable=False)
    payer_email = Column(String(100), nullable=False)
    receipt_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
