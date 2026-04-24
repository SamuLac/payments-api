"""
Receipts Router

Handles receipt file uploads to AWS S3.

  POST   /receipts/{payment_id}/upload   - Upload a receipt for a payment
  DELETE /receipts/{payment_id}          - Remove receipt from a payment
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.schemas.payment import PaymentResponse
from app.services.s3_service import upload_receipt_to_s3, delete_receipt_from_s3

router = APIRouter()


@router.post(
    "/{payment_id}/upload",
    response_model=PaymentResponse,
    summary="Upload receipt",
    description="""
Uploads a receipt file (JPEG, PNG or PDF) to AWS S3 and links it to the payment.

**Accepted formats:** JPEG, PNG, PDF  
**Max file size:** 5MB (enforced at the reverse proxy level)

The file is stored at:  
`s3://{bucket}/receipts/{payment_id}/{timestamp}_{filename}`
    """,
)
async def upload_receipt(
    payment_id: UUID,
    file: UploadFile = File(..., description="Receipt file (JPEG, PNG or PDF, max 5MB)"),
    db: Session = Depends(get_db),
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment '{payment_id}' not found.",
        )

    receipt_url = upload_receipt_to_s3(file, str(payment_id))

    payment.receipt_url = receipt_url
    db.commit()
    db.refresh(payment)

    return payment


@router.delete(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Remove receipt",
    description="Removes the receipt linked to a payment, deleting the file from S3.",
)
def remove_receipt(payment_id: UUID, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment '{payment_id}' not found.",
        )

    if not payment.receipt_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This payment has no receipt attached.",
        )

    delete_receipt_from_s3(payment.receipt_url)

    payment.receipt_url = None
    db.commit()
    db.refresh(payment)

    return payment
