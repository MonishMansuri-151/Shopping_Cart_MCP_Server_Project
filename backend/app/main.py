from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.products import router as products_router
from app.api.cart import router as cart_router
from app.api.checkout import router as checkout_router

from app.logging_config import setup_logging

from app.ai.assistant import chat_with_shopping_assistant

import logging


# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------

setup_logging()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------------

app = FastAPI(
    title="Shopping Cart API",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# EXISTING ROUTERS
# ---------------------------------------------------------

app.include_router(products_router)
app.include_router(cart_router)
app.include_router(checkout_router)


# ---------------------------------------------------------
# BASIC ENDPOINTS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# EXISTING MCP CLIENT ENDPOINTS
# ---------------------------------------------------------

from fastmcp import Client

MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"
import json

@app.get("/mcp/products")
async def mcp_products():
    async with Client(MCP_SERVER_URL) as client:
        result = await client.call_tool("get_products", {})

        return json.loads(result.content[0].text)

# @app.get("/mcp/products")
# async def mcp_products():

#     async with Client(MCP_SERVER_URL) as client:

#         result = await client.call_tool(
#             "get_products",
#             {}
#         )

#         return result.data if hasattr(result, "data") else result
# @app.get("/mcp/products")
# async def mcp_products():
#     async with Client(MCP_SERVER_URL) as client:
#         result = await client.call_tool("get_products", {})
#         print("MCP RESULT:", result)
#         print("MCP RESULT TYPE:", type(result))
#         return {"result": str(result)}

@app.get("/mcp/cart")
async def mcp_cart():

    async with Client(MCP_SERVER_URL) as client:

        result = await client.call_tool(
            "get_cart",
            {}
        )

        return result.data if hasattr(result, "data") else result


@app.post("/mcp/cart/add")
async def mcp_add_to_cart(
    product_id: int,
    quantity: int = 1
):

    async with Client(MCP_SERVER_URL) as client:

        result = await client.call_tool(
            "add_to_cart",
            {
                "product_id": product_id,
                "quantity": quantity
            }
        )

        return result.data if hasattr(result, "data") else result


@app.post("/mcp/checkout")
async def mcp_checkout():

    async with Client(MCP_SERVER_URL) as client:

        result = await client.call_tool(
            "checkout",
            {}
        )

        return result.data if hasattr(result, "data") else result


# ---------------------------------------------------------
# AI CHAT
# ---------------------------------------------------------

class ChatRequest(BaseModel):

    message: str


@app.post("/chat")
async def chat(request: ChatRequest):

    logger.info(
        "AI chat request: %s",
        request.message
    )

    result = await chat_with_shopping_assistant(
        request.message
    )

    logger.info(
        "AI response generated successfully"
    )

    return result