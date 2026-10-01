from fastapi import APIRouter, HTTPException
from app.database.connection import get_db_connection

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/")
def checkout():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            cart.product_id,
            cart.quantity,
            products.price,
            products.stock,
            products.name
        FROM cart
        JOIN products ON cart.product_id = products.id
    """)

    items = cursor.fetchall()

    if not items:
        cursor.close()
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total = 0

    for item in items:
        if item["quantity"] > item["stock"]:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {item['name']}"
            )

        total += float(item["price"]) * item["quantity"]

    for item in items:
        cursor.execute(
            """
            UPDATE products
            SET stock = stock - %s
            WHERE id = %s
            """,
            (item["quantity"], item["product_id"])
        )

    cursor.execute("DELETE FROM cart")

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Order placed successfully",
        "total": total
    }