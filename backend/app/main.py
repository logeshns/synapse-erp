from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}

@app.get("/force-seed")
def force_seed():
    from app.db.database import SessionLocal
    from app.models.user import User
    import bcrypt
    
    db = SessionLocal()
    try:
        # Generate hash directly with native bcrypt
        hashed_pw = bcrypt.hashpw("Demo@12345".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        accounts = [
            {"name": "Demo Owner", "email": "owner@demo.com", "role": "OWNER"},
            {"name": "Demo Sales", "email": "sales@demo.com", "role": "SALES"},
            {"name": "Demo Warehouse", "email": "warehouse@demo.com", "role": "WAREHOUSE"},
            {"name": "Demo Accountant", "email": "accountant@demo.com", "role": "ACCOUNTANT"},
            {"name": "Demo Manager", "email": "manager@demo.com", "role": "MANAGER"},
        ]
        
        for acc in accounts:
            user = db.query(User).filter(User.email == acc["email"]).first()
            if user:
                user.password_hash = hashed_pw  # Safely overwrite the broken hash
            else:
                db.add(User(name=acc["name"], email=acc["email"], password_hash=hashed_pw, role=acc["role"], is_active=True))
                
        db.commit()
        return {"message": "✨ Passwords completely overwritten and successfully updated!"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()