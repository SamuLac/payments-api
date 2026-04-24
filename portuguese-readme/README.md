# 💳 Payments API

API REST de processamento de pagamentos construída com **FastAPI**, **PostgreSQL** e **AWS S3** para armazenamento de comprovantes.

> Projeto de portfólio para demonstrar habilidades de desenvolvimento backend em Python.

---

## 🚀 Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Framework | FastAPI |
| Banco de Dados | PostgreSQL + SQLAlchemy ORM |
| Armazenamento | AWS S3 (boto3) |
| Validação | Pydantic v2 |
| Testes | Pytest |
| Deploy | Docker + Docker Compose |

---

## ✨ Funcionalidades

- ✅ CRUD completo de pagamentos
- ✅ Máquina de estados para status do pagamento (pendente → concluído → estornado)
- ✅ Upload de comprovantes para AWS S3 (JPEG, PNG, PDF)
- ✅ Paginação e filtros por status e método de pagamento
- ✅ Documentação OpenAPI gerada automaticamente (Swagger UI)
- ✅ Validação de entrada com mensagens de erro claras
- ✅ Suite de testes completa com SQLite em memória

---

## 🏃 Rodando localmente

### 1. Clone e configure

```bash
git clone https://github.com/SamuLac/payments-api
cd payments-api

cp .env.example .env
# Edite o .env com suas credenciais AWS e nome do bucket
```

### 2. Rodando com Docker Compose

```bash
docker-compose up --build
```

API disponível em: **http://localhost:8000**  
Documentação interativa: **http://localhost:8000/docs**

### 3. Rodando sem Docker (manual)

```bash
python -m venv .venv
source .venv/bin/activate   
# Windows: .venv\Scripts\activate or .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Certifique-se de que o PostgreSQL está rodando, depois:
uvicorn app.main:app --reload
```

---

## 🧪 Rodando os testes

```bash
pytest tests/ -v
```

Os testes usam SQLite em memória — nenhuma configuração adicional necessária.

OBS: Não implementado ainda

---

## 📖 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Health check |
| GET | `/payments` | Lista pagamentos (paginado, com filtros) |
| POST | `/payments` | Cria um novo pagamento |
| GET | `/payments/{id}` | Busca pagamento por ID |
| PATCH | `/payments/{id}` | Atualiza status do pagamento |
| DELETE | `/payments/{id}` | Remove um pagamento |
| POST | `/receipts/{id}/upload` | Faz upload do comprovante para o S3 |
| DELETE | `/receipts/{id}` | Remove o comprovante |

Documentação interativa completa disponível em `/docs` (Swagger UI).

---

## ☁️ Configuração do AWS S3

1. Crie um bucket S3 na sua conta AWS
2. Crie um usuário IAM com a policy `AmazonS3FullAccess` (ou uma policy com escopo reduzido)
3. Copie o Access Key ID e o Secret para o seu arquivo `.env`
4. Defina o `S3_BUCKET_NAME` no `.env`

> **Dica para produção:** Em EC2 ou Lambda, use IAM Roles no lugar de chaves de acesso.

---

## 📁 Estrutura do Projeto

```
payments-api/
├── app/
│   ├── main.py           # Configuração do FastAPI, middlewares e routers
│   ├── database.py       # Engine e sessão do SQLAlchemy
│   ├── models/
│   │   └── payment.py    # Model ORM do pagamento
│   ├── schemas/
│   │   └── payment.py    # Schemas Pydantic (request/response)
│   ├── routers/
│   │   ├── payments.py   # Endpoints CRUD de pagamentos
│   │   └── receipts.py   # Endpoints de upload para o S3
│   └── services/
│       └── s3_service.py # Integração com AWS S3
├── tests/
│   └── test_payments.py  # Suite de testes completa
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```
