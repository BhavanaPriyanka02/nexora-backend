from app.database import engine
from app.models import Base

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.products import router as products_router
from app.routes.cart import router as cart_router
from app.routes.orders import router as orders_router
from app.routes.auth import router as auth_router

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# ✅ Allowed frontend URLs
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://nexora-frontend-woad.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(products_router, prefix="/products")
app.include_router(cart_router, prefix="/cart")
app.include_router(orders_router, prefix="/orders")
app.include_router(auth_router, prefix="/auth")

@app.get("/")
def root():
    return {"message": "Backend is running"}
