# from fastapi import FastAPI
# from app.database.connection import get_db_connection
# from app.api.products import router as products_router
# from app.api.checkout import router as checkout_router
# from app.api.cart import router as cart_router
# from app.logging_config import setup_logging
# setup_logging()
# app = FastAPI(title="Shopping Cart API")


# @app.get("/")
# def home():
#     return {
#         "message": "Shopping Cart API is running"
#     }
# app.include_router(products_router)
# app.include_router(cart_router)
# app.include_router(checkout_router)

# @app.get("/test-db")
# def test_database():
#     connection = get_db_connection()

#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM products")

#     products = cursor.fetchall()

#     cursor.close()
#     connection.close()

#     return {
#         "products": products
#     }
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.products import router as products_router
from app.api.cart import router as cart_router
from app.api.checkout import router as checkout_router
from app.logging_config import setup_logging


setup_logging()

app = FastAPI(
    title="Shopping Cart API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Shopping Cart API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(products_router)
app.include_router(cart_router)
app.include_router(checkout_router)