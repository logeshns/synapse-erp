from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from app.api.routes.ai import router as ai_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.customers import router as customers_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.invoices import router as invoices_router
from app.api.routes.manager import router as manager_router
from app.api.routes.order_requests import router as order_requests_router
from app.api.routes.orders import router as orders_router
from app.api.routes.payments import router as payments_router
from app.api.routes.products import router as products_router
from app.api.routes.receipts import router as receipts_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_id import RequestIdMiddleware

# Imports for auto-creating tables and seeding demo user
from app.db.database import Base, engine, SessionLocal
from app.models.user import User

configure_logging()
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=[settings.FRONTEND_URL], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(order_requests_router)
app.include_router(orders_router)
app.include_router(invoices_router)
app.include_router(payments_router)
app.include_router(receipts_router)
app.include_router(ai_router)
app.include_router(analytics_router)
app.include_router(manager_router)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def startup_event():
    # Automatically create tables on startup (no Alembic needed)
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed the demo owner account if it doesn't exist
    db = SessionLocal()
    try:
        owner = db.query(User).filter(User.email == "owner@demo.com").first()
        if not owner:
            hashed_password = pwd_context.hash("Demo@12345")
            demo_user = User(
                name="Demo Owner",
                email="owner@demo.com",
                password_hash=hashed_password,
                role="OWNER",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            print("🚀 Demo user 'owner@demo.com' automatically seeded!")
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}