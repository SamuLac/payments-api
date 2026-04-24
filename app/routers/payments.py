"""
Payments Router

Defines all payment-related endpoints:
  GET    /payments          - List payments (with pagination and filters)
  POST   /payments          - Create a new payment
  GET    /payments/{id}     - Get a specific payment
  PATCH  /payments/{id}     - Update payment status
  DELETE /payments/{id}     - Delete a payment
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
)

router = APIRouter()


@router.get(
    "",
    response_model=PaymentListResponse,
    summary="List payments",
    description="Returns a paginated list of payments. Supports filtering by status and payment method.",
)
def list_payments(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of results per page"),
    status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    method: Optional[str] = Query(None, description="Filter by payment method"),
    db: Session = Depends(get_db),
):
    query = db.query(Payment)

    if status:
        query = query.filter(Payment.status == status)
    if method:
        query = query.filter(Payment.method == method)

    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaymentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=results,
    )


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment",
    description="Creates a new payment with status 'pending'. Use PATCH to update the status after processing.",
)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    payment = Payment(**payload.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get payment by ID",
    description="Returns a single payment by its UUID.",
)
def get_payment(payment_id: UUID, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment '{payment_id}' not found.",
        )
    return payment


@router.patch(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Update payment status",
    description="""
Updates the status of an existing payment.

**Allowed transitions:**
- `pending` → `completed` or `failed`
- `completed` → `refunded`
- `failed` → `pending` (retry)
    """,
)
def update_payment(
    payment_id: UUID, payload: PaymentUpdate, db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment '{payment_id}' not found.",
        )

    valid_transitions = {
        PaymentStatus.PENDING: [PaymentStatus.COMPLETED, PaymentStatus.FAILED],
        PaymentStatus.COMPLETED: [PaymentStatus.REFUNDED],
        PaymentStatus.FAILED: [PaymentStatus.PENDING],
        PaymentStatus.REFUNDED: [],
    }

    if payload.status not in valid_transitions[payment.status]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot transition from '{payment.status}' to '{payload.status}'.",
        )

    payment.status = payload.status
    db.commit()
    db.refresh(payment)
    return payment


@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete payment",
    description="Deletes a payment. Only payments with status 'pending' or 'failed' can be deleted.",
)
def delete_payment(payment_id: UUID, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment '{payment_id}' not found.",
        )

    if payment.status not in [PaymentStatus.PENDING, PaymentStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only 'pending' or 'failed' payments can be deleted.",
        )

    db.delete(payment)
    db.commit()
