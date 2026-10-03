
from fastmcp import FastMCP
import mysql.connector
import os
from dotenv import load_dotenv

# Project root
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# backend/.env
ENV_PATH = os.path.join(
    BASE_DIR,
    "backend",
    ".env"
)

load_dotenv(ENV_PATH)
print("DB_HOST =", os.getenv("DB_HOST"))
print("DB_USER =", os.getenv("DB_USER"))
print("DB_NAME =", os.getenv("DB_NAME"))
print("PASSWORD LOADED =", bool(os.getenv("DB_PASSWORD")))

mcp = FastMCP("Shopping Cart MCP Server")

# # ---------------------------------------------------------
# # DATABASE CONNECTION
# # ---------------------------------------------------------

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.getenv("DB_HOST"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         database=os.getenv("DB_NAME")
#     )

def get_db_connection():
    print("DB_HOST:", os.getenv("DB_HOST"))
    print("DB_USER:", os.getenv("DB_USER"))
    print("DB_NAME:", os.getenv("DB_NAME"))
    print("DB_PASSWORD loaded:", bool(os.getenv("DB_PASSWORD")))

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
# ---------------------------------------------------------
# GET PRODUCTS
# ---------------------------------------------------------

@mcp.tool()
def get_products():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, category, price, stock
        FROM products
    """)

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products


# ---------------------------------------------------------
# GET CART
# ---------------------------------------------------------

@mcp.tool()
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
            products.price * cart.quantity AS subtotal
        FROM cart
        JOIN products
        ON cart.product_id = products.id
    """)

    cart = cursor.fetchall()

    cursor.close()
    connection.close()

    return cart


# ---------------------------------------------------------
# ADD TO CART
# ---------------------------------------------------------

@mcp.tool()
def add_to_cart(product_id: int, quantity: int = 1):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Check product
    cursor.execute(
        """
        SELECT id, name, stock
        FROM products
        WHERE id = %s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:

        cursor.close()
        connection.close()

        return {
            "error": "Product not found"
        }

    if quantity <= 0:

        cursor.close()
        connection.close()

        return {
            "error": "Quantity must be greater than 0"
        }

    # Check existing cart item
    cursor.execute(
        """
        SELECT id, quantity
        FROM cart
        WHERE product_id = %s
        """,
        (product_id,)
    )

    existing = cursor.fetchone()

    if existing:

        new_quantity = existing["quantity"] + quantity

        if new_quantity > product["stock"]:

            cursor.close()
            connection.close()

            return {
                "error": "Not enough stock"
            }

        cursor.execute(
            """
            UPDATE cart
            SET quantity = %s
            WHERE id = %s
            """,
            (new_quantity, existing["id"])
        )

    else:

        if quantity > product["stock"]:

            cursor.close()
            connection.close()

            return {
                "error": "Not enough stock"
            }

        cursor.execute(
            """
            INSERT INTO cart (product_id, quantity)
            VALUES (%s, %s)
            """,
            (product_id, quantity)
        )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": f"{product['name']} added to cart",
        "product_id": product_id,
        "quantity_added": quantity
    }


# ---------------------------------------------------------
# CHECKOUT
# ---------------------------------------------------------

@mcp.tool()
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
        JOIN products
        ON cart.product_id = products.id
    """)

    items = cursor.fetchall()

    if not items:

        cursor.close()
        connection.close()

        return {
            "error": "Cart is empty"
        }

    total = 0

    # Check stock and calculate total
    for item in items:

        if item["quantity"] > item["stock"]:

            cursor.close()
            connection.close()

            return {
                "error": f"Not enough stock for {item['name']}"
            }

        total += float(item["price"]) * item["quantity"]

    # Reduce stock
    for item in items:

        cursor.execute(
            """
            UPDATE products
            SET stock = stock - %s
            WHERE id = %s
            """,
            (
                item["quantity"],
                item["product_id"]
            )
        )

    # Empty cart
    cursor.execute("DELETE FROM cart")

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Order placed successfully",
        "total": total
    }


# ---------------------------------------------------------
# START MCP SERVER
# ---------------------------------------------------------

if __name__ == "__main__":

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8001
    )