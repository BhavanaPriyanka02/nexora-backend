from fastapi import APIRouter, Depends, HTTPException
from app.models import Order, OrderItem, Product
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, admin_required
from app.models import OrderStatus
from app.schemas.common import APIResponse
from app.schemas.order import OrderResponse


router = APIRouter()

allowed_transitions = {
    OrderStatus.pending: [OrderStatus.paid, OrderStatus.cancelled],
    OrderStatus.paid: [OrderStatus.shipped],
    OrderStatus.shipped: [OrderStatus.delivered],
    OrderStatus.delivered: [],
    OrderStatus.cancelled: []
}

@router.post("/create", response_model=APIResponse)
def create_order(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    print("Incoming cart:", data)

    idempotency_key = data.get("idempotency_key")

    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency key required")

    # 🔥 CHECK IF ORDER ALREADY EXISTS
    existing_order = db.query(Order).filter(
        Order.idempotency_key == idempotency_key
    ).first()

    if existing_order:
        print("Duplicate request detected — returning existing order")
        return existing_order

    items = data.get("items", [])

    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_price = 0

    new_order = Order(
        user_id=current_user.id,
        status=OrderStatus.pending,
        total_price=0,
        idempotency_key=idempotency_key
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)


    # Loop through cart items
    for item in items:
        product = db.query(Product).filter(Product.id == item["id"]).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < item["quantity"]:
            raise HTTPException(status_code=400, detail="Not enough stock")

        line_total = product.price * item["quantity"]
        total_price += line_total

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item["quantity"],
            price=product.price
        )

        db.add(order_item)

        # Reduce stock
        product.stock -= item["quantity"]

    new_order.total_price = total_price

    db.commit()
    db.refresh(new_order)

    return {
    "success": True,
    "message": "Order created successfully",
    "data": {
        "id": new_order.id,
        "status": new_order.status,
        "total_price": new_order.total_price
    }
}

@router.get("/my-orders", response_model=APIResponse)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()

    result = []

    for order in orders:
        order_data = {
            "id": order.id,
            "status": order.status,
            "total_price": order.total_price,
            "items": []
        }

        for item in order.items:
            order_data["items"].append({
                "product_id": item.product.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.price
            })

        result.append(order_data)

    return {
    "success": True,
    "message": "Orders fetched successfully",
    "data": result
}




# 🔐 Admin: Get All Orders
@router.get("/")
def get_all_orders(
    db: Session = Depends(get_db),
    user: dict = Depends(admin_required)
):
    return db.query(Order).all()

@router.put("/{order_id}/cancel", response_model=APIResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Only owner can cancel
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Prevent double cancel
    if order.status == OrderStatus.cancelled:
        raise HTTPException(status_code=400, detail="Order already cancelled")

    # Prevent cancelling shipped or delivered orders
    if order.status in [OrderStatus.shipped, OrderStatus.delivered]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel shipped or delivered order"
        )

    # Restore stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock += item.quantity

    order.status = OrderStatus.cancelled


    db.commit()

    return {
    "success": True,
    "message": "Order cancelled successfully",
    "data": None
}

@router.put("/{order_id}/status", response_model=APIResponse)
def update_order_status(
    order_id: int,
    data: dict,
    db: Session = Depends(get_db),
    admin = Depends(admin_required)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        new_status = OrderStatus(data["status"])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value")

    if new_status not in allowed_transitions[order.status]:
        raise HTTPException(status_code=400, detail="Invalid transition")

    order.status = new_status
    db.commit()
    db.refresh(order)

    return {
        "success": True,
        "message": "Order status updated successfully",
        "data": {
            "id": order.id,
            "status": order.status
        }
    }



