from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, users, categories, suppliers, products, stock, alerts, reports, dashboard

app = FastAPI(title="InventoryPulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(stock.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}
