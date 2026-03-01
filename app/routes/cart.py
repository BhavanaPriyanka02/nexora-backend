from fastapi import APIRouter

router = APIRouter()

# cart structure: { product_id: quantity }
cart_items = {}

@router.post("/add")
def add_to_cart(item: dict):
    product_id = item["product_id"]

    if product_id in cart_items:
        cart_items[product_id] += 1
    else:
        cart_items[product_id] = 1

    return {"message": "Item added", "cart": cart_items}

@router.get("/")
def get_cart():
    return {
        "items": [
            {"product_id": pid, "quantity": qty}
            for pid, qty in cart_items.items()
        ]
    }

@router.post("/clear")
def clear_cart():
    cart_items.clear()
    return {"message": "Cart cleared"}
