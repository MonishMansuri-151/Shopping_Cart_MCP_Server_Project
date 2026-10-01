import logging

from fastapi import APIRouter
from app.database.connection import get_db_connection


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

logger = logging.getLogger(__name__)


@router.get("/")
def get_products():

    logger.info("Fetching products")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, category, price, stock
        FROM products
    """)

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    logger.info("Products fetched successfully")

    return products