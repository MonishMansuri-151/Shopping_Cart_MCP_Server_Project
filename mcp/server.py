from mcp.server.fastmcp import FastMCP
import requests


mcp = FastMCP("Shopping Cart MCP")

API_URL = "http://127.0.0.1:8000"


@mcp.tool()
def get_products():
    """Get all products from the shopping cart."""
    response = requests.get(
        f"{API_URL}/products/"
    )

    response.raise_for_status()

    return response.json()


@mcp.tool()
def add_to_cart(
    product_id: int,
    quantity: int = 1
):
    """Add a product to the shopping cart."""

    response = requests.post(
        f"{API_URL}/cart/add",
        json={
            "product_id": product_id,
            "quantity": quantity
        }
    )

    response.raise_for_status()

    return response.json()


@mcp.tool()
def get_cart():
    """Get all items currently in the cart."""

    response = requests.get(
        f"{API_URL}/cart/"
    )

    response.raise_for_status()

    return response.json()


@mcp.tool()
def checkout():
    """Complete the current shopping cart checkout."""

    response = requests.post(
        f"{API_URL}/checkout/"
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    mcp.run()