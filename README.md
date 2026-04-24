# 💳 Payments API

A simplified payment processing REST API built with **FastAPI**, **PostgreSQL** and **AWS S3** for receipt storage.

There is a readme file in pt-br below.

> Built as a portfolio project to demonstrate backend skills in Python.

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| File Storage | AWS S3 (boto3) |
| Validation | Pydantic v2 |
| Tests | Pytest |
| Deploy | Docker + Docker Compose |

---

## ✨ Features

- ✅ Full CRUD for payments
- ✅ Payment status state machine (pending → completed → refunded)
- ✅ Receipt upload to AWS S3 (JPEG, PNG, PDF)
- ✅ Pagination and filtering by status/method
- ✅ Auto-generated OpenAPI docs (Swagger UI)
- ✅ Input validation with clear error messages
- ✅ Full test suite with in-memory SQLite

---

## 🏃 Running locally

### 1. Clone and configure

```bash
git clone https://github.com/SamuLac/payments-api
cd payments-api

cp .env.example .env
# Edit .env with your AWS credentials and bucket name
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

API will be available at: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

### 3. Run without Docker (manual)

```bash
python -m venv venv
source .venv/bin/activate   
# Windows: .venv\Scripts\activate or .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Make sure PostgreSQL is running, then:
uvicorn app.main:app --reload
```

---

## 🧪 Running tests

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database — no setup needed.

Not implemented at this time

---

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/payments` | List payments (paginated, filterable) |
| POST | `/payments` | Create a new payment |
| GET | `/payments/{id}` | Get payment by ID |
| PATCH | `/payments/{id}` | Update payment status |
| DELETE | `/payments/{id}` | Delete payment |
| POST | `/receipts/{id}/upload` | Upload receipt to S3 |
| DELETE | `/receipts/{id}` | Remove receipt |

Full interactive documentation available at `/docs` (Swagger UI).

---

## ☁️ AWS S3 Setup

1. Create an S3 bucket in your AWS account
2. Create an IAM user with `AmazonS3FullAccess` (or a scoped policy)
3. Copy the access key and secret to your `.env` file
4. Set `S3_BUCKET_NAME` in `.env`

> **Production tip:** On EC2 or Lambda, use IAM Roles instead of access keys.

---

## 📁 Project Structure

```
payments-api/
├── app/
│   ├── main.py           # FastAPI app, middleware, router registration
│   ├── database.py       # SQLAlchemy engine and session
│   ├── models/
│   │   └── payment.py    # Payment ORM model
│   ├── schemas/
│   │   └── payment.py    # Pydantic schemas (request/response)
│   ├── routers/
│   │   ├── payments.py   # Payment CRUD endpoints
│   │   └── receipts.py   # S3 upload endpoints
│   └── services/
│       └── s3_service.py # AWS S3 integration
├── tests/
│   └── test_payments.py  # Full test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```
