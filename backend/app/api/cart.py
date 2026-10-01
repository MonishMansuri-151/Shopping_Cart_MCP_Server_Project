from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.connection import get_db_connection

router = APIRouter(prefix="/cart", tags=["Cart"])


class CartItem(BaseModel):
    product_id: int
    quantity: int = 1


@router.get("/")
def get_cart():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            cart.id,
            cart.product_id,
            products.name,
            products.price,
            cart.quantity,
            (products.price * cart.quantity) AS subtotal
        FROM cart
        JOIN products ON cart.product_id = products.id
    """)

    items = cursor.fetchall()

    cursor.close()
    connection.close()

    return items


@router.post("/add")
def add_to_cart(item: CartItem):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, stock FROM products WHERE id = %s",
        (item.product_id,)
    )

    product = cursor.fetchone()

    if not product:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Product not found")

    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    cursor.execute(
        "SELECT id, quantity FROM cart WHERE product_id = %s",
        (item.product_id,)
    )

    existing = cursor.fetchone()

    if existing:
        new_quantity = existing["quantity"] + item.quantity

        if new_quantity > product["stock"]:
            raise HTTPException(
                status_code=400,
                detail="Not enough stock"
            )

        cursor.execute(
            "UPDATE cart SET quantity = %s WHERE id = %s",
            (new_quantity, existing["id"])
        )
    else:
        if item.quantity > product["stock"]:
            raise HTTPException(
                status_code=400,
                detail="Not enough stock"
            )

        cursor.execute(
            """
            INSERT INTO cart (product_id, quantity)
            VALUES (%s, %s)
            """,
            (item.product_id, item.quantity)
        )

    connection.commit()

    cursor.close()
    connection.close()

    return {"message": "Product added to cart"}


@router.delete("/{cart_id}")
def remove_from_cart(cart_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM cart WHERE id = %s",
        (cart_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {"message": "Item removed from cart"}