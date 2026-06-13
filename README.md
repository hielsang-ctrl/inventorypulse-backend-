# InventoryPulse Backend

FastAPI-based REST API for inventory management.

## Quick Start (Docker)

```bash
cp .env.example .env
docker-compose up --build
```

API available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

Default admin credentials: `admin@inventorypulse.com` / `Admin@1234`

## Local Development

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set your DATABASE_URL
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

## Run Tests

```bash
pytest tests/ -v --cov=app
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/login | — | Login, returns JWT |
| POST | /auth/refresh | Any | Refresh token |
| GET | /dashboard/summary | Any | KPI summary |
| GET/POST | /products | Any/Admin | List / create products |
| PUT/DELETE | /products/{id} | Admin | Update / deactivate |
| GET/POST | /categories | Any/Admin | Categories |
| GET/POST | /suppliers | Any/Admin | Suppliers |
| POST | /stock/in | Any | Record stock receipt |
| POST | /stock/out | Any | Record stock dispatch |
| GET | /stock/movements | Any | Movement history |
| GET | /alerts | Any | Active low-stock alerts |
| POST | /alerts/{id}/resolve | Admin | Resolve alert |
| GET | /reports/inventory-valuation | Any | Stock value report |
| GET | /reports/stock-movement-summary | Any | Movement summary |
| GET | /reports/export/csv | Any | Export inventory CSV |
| GET/POST | /users | Admin | User management |

## Project Structure

```
app/
├── main.py           # FastAPI app + CORS + routers
├── config.py         # Settings from .env
├── database.py       # SQLAlchemy engine & session
├── dependencies.py   # JWT auth, role guards
├── models/           # ORM models
├── schemas/          # Pydantic schemas
├── routers/          # Route handlers
└── services/         # Business logic (alert evaluation)
alembic/              # DB migrations
tests/                # Pytest tests
seed.py               # Initial data seed
```
