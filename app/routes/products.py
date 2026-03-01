from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from app.auth import admin_required
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.common import APIResponse


router = APIRouter()

@router.get("/", response_model=APIResponse)
def get_products(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    total = db.query(Product).count()
    products = db.query(Product).offset(skip).limit(limit).all()

    product_list = [
        ProductResponse.model_validate(product)
        for product in products
    ]

    return {
    "success": True,
    "message": "Products fetched successfully",
    "data": {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": product_list
    }
}



@router.post("/", response_model=APIResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(admin_required)
):
    new_product = Product(**product.dict())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
    "success": True,
    "message": "Product created successfully",
    "data": ProductResponse.model_validate(new_product)
}


@router.put("/{product_id}", response_model=APIResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(admin_required)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    return {
    "success": True,
    "message": "Product updated successfully",
    "data": ProductResponse.model_validate(db_product)
}


@router.delete("/{product_id}", response_model=APIResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(admin_required)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()

    return {
    "success": True,
    "message": "Product deleted successfully",
    "data": None
}
