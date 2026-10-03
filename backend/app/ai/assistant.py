import json
import logging
import os

from dotenv import load_dotenv
from fastmcp import Client
from groq import AsyncGroq

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing in .env")

groq_client = AsyncGroq(
    api_key=GROQ_API_KEY
)

MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"

MODEL = "openai/gpt-oss-120b"


MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_products",
            "description": "Get all products including name, category, price and stock.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cart",
            "description": "Get all items currently present in the shopping cart.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Add a product to the shopping cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "Product ID"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity to add"
                    }
                },
                
                "required": ["product_id", "quantity"]
            }
        }
    },
   
      {
    "type": "function",
    "function": {
        "name": "checkout",
        "description": "Checkout the shopping cart. This tool takes no arguments.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    }
}
]



async def execute_mcp_tool(tool_name, arguments):

    logger.info(
        "Calling MCP tool: %s | arguments=%s",
        tool_name,
        arguments
    )

    async with Client(MCP_SERVER_URL) as client:

        result = await client.call_tool(
            tool_name,
            arguments
        )

        logger.info("Raw MCP result: %s", result)

        # FastMCP 3.x result handling
        if hasattr(result, "content") and result.content:
            text = result.content[0].text

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

        return result

async def chat_with_shopping_assistant(user_message: str):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a shopping cart assistant. "
                "You can help users with products, stock, cart and checkout. "
                "Use MCP tools whenever real shopping information is required. "
                "Never invent product names, prices, stock, cart contents or totals. "
                "If product ID is unknown, use get_products first. "
                "Understand English, Hindi and Hinglish. "
                "Give short and friendly answers."
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    # Maximum 3 tool-call rounds
    for _ in range(3):

        response = await groq_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=MCP_TOOLS,
            tool_choice="auto",
            temperature=0.2
        )

        assistant_message = response.choices[0].message

        # No tool call -> final answer
        if not assistant_message.tool_calls:

            return {
                "reply": assistant_message.content
            }

        # Add assistant tool-call message
        messages.append(assistant_message)

        # Execute every requested tool
        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments or "{}"
                )
            except json.JSONDecodeError:

                arguments = {}

            logger.info(
                "AI requested MCP tool: %s",
                tool_name
            )

            try:

                tool_result = await execute_mcp_tool(
                    tool_name,
                    arguments
                )

                logger.info(
                    "MCP tool result: %s",
                    tool_result
                )

            except Exception as error:

                logger.exception(
                    "MCP tool failed"
                )

                tool_result = {
                    "error": str(error)
                }

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(
                        tool_result,
                        default=str
                    )
                }
            )

    return {
        "reply": "I couldn't complete the request right now. Please try again."
    }