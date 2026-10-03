# Shopping Cart + MySQL + FastAPI + MCP + Groq AI

## 1. Project Overview

This project is a complete shopping cart application built with:

-   **Frontend:** HTML, CSS, JavaScript
-   **Backend:** FastAPI
-   **Database:** MySQL
-   **MCP:** FastMCP server and FastMCP client
-   **AI:** Groq LLM (`openai/gpt-oss-120b`)
-   **Logging:** Python logging with `logs/app.log`
-   **Testing:** API and application test files

The main goal of the project is to demonstrate how a normal shopping
cart application can be connected to an **MCP server** and an **AI
assistant**.

The application supports:

-   Viewing products
-   Adding products to cart
-   Viewing cart
-   Removing cart items
-   Checkout
-   Updating product stock after checkout
-   Asking the AI assistant about products and cart
-   Using MCP tools from the AI assistant
-   Logging application activity

------------------------------------------------------------------------

# 2. Complete Architecture

## Normal Shopping Cart Flow

``` text
User
 |
 v
Frontend (HTML/CSS/JavaScript)
 |
 | HTTP REST API
 v
FastAPI Backend :8000
 |
 +--------------------+
 |                    |
 v                    v
Products API       Cart API / Checkout API
 |                    |
 +----------+---------+
            |
            v
        MySQL Database
        shopping_cart
```

## AI + MCP Flow

The main architecture of this project is:

``` text
                         AI SHOPPING FLOW

User
 |
 v
Frontend AI Chat
 |
 | POST /chat
 v
FastAPI
 |
 v
Groq LLM
 |
 | Tool call
 v
FastMCP Client
 |
 | HTTP
 v
MCP Server :8001
 |
 v
MCP Tool
 |
 v
MySQL Database
 |
 | Tool Result
 v
MCP Server
 |
 v
FastMCP Client
 |
 v
Groq LLM
 |
 | Final natural-language answer
 v
FastAPI
 |
 v
Frontend
```

### Example

User asks:

``` text
What is the price of MacBook Pro?
```

The flow is:

``` text
User
  ↓
/chat
  ↓
Groq
  ↓
get_products tool
  ↓
MCP Client
  ↓
MCP Server
  ↓
MySQL
  ↓
MacBook Pro = ₹129999
  ↓
MCP result
  ↓
Groq
  ↓
"MacBook Pro is priced at ₹129,999."
```

The AI does not invent the price. It gets the information from the MCP
tool, which gets it from MySQL.

------------------------------------------------------------------------

# 3. Project Folder Structure

``` text
Shopping_Cart_mcp_server/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   └── assistant.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── products.py
│   │   │   ├── cart.py
│   │   │   └── checkout.py
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── connection.py
│   │   │
│   │   └── logging_config.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── mcp/
│   ├── server.py
│   └── requirements.txt
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── logs/
│   └── app.log
│
├── monitoring/
│   └── README.md
│
├── tests/
│   ├── test_products.py
│   ├── test_cart.py
│   └── test_checkout.py
│
├── .gitignore
├── README.md
└── .env.example
```

------------------------------------------------------------------------

# 4. Technologies Used

  Technology      Purpose
  --------------- --------------------------------------
  HTML            Frontend structure
  CSS             Frontend design
  JavaScript      Frontend functionality and API calls
  FastAPI         Backend REST API
  MySQL           Product, cart and stock data
  FastMCP         MCP server/client communication
  Groq            AI/LLM
  Python          Backend, MCP and AI integration
  Uvicorn         FastAPI server
  python-dotenv   Environment variables
  Logging         Application monitoring/logs

------------------------------------------------------------------------

# 5. Database

Database name:

``` text
shopping_cart
```

## Products table

``` sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Cart table

``` sql
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);
```

## Current product data

The working database contains:

    ID Product               Category           Price              Stock
  ---- --------------------- ------------- ---------- ------------------
    10 MacBook Pro           LAPTOP          ₹129,999   Current DB value
    11 Wireless Mouse        ACCESSORIES       ₹1,499   Current DB value
    12 Mechanical Keyboard   ACCESSORIES       ₹4,999   Current DB value

Stock changes after cart checkout.

### Important database limitation

The current database does not contain `orders` or `order_items` tables.

Therefore checkout:

1.  Reads the cart
2.  Checks stock
3.  Calculates total
4.  Decreases product stock
5.  Deletes cart rows

It does **not** permanently store order history.

------------------------------------------------------------------------

# 6. Backend REST APIs

FastAPI runs on:

``` text
http://127.0.0.1:8000
```

## Product API

``` http
GET /products/
```

Returns available products.

Example:

``` json
[
  {
    "id": 10,
    "name": "MacBook Pro",
    "category": "LAPTOP",
    "price": 129999,
    "stock": 8
  }
]
```

------------------------------------------------------------------------

## Get Cart

``` http
GET /cart/
```

Returns current cart items and subtotals.

------------------------------------------------------------------------

## Add to Cart

``` http
POST /cart/add
```

Example request:

``` json
{
  "product_id": 11,
  "quantity": 2
}
```

The backend:

1.  Checks whether product exists
2.  Checks requested quantity
3.  Checks available stock
4.  Checks whether product already exists in cart
5.  Updates existing quantity or inserts a new row

------------------------------------------------------------------------

## Remove From Cart

``` http
DELETE /cart/{cart_id}
```

Removes a cart item.

------------------------------------------------------------------------

## Checkout

``` http
POST /checkout/
```

The checkout process:

``` text
Read cart
   ↓
Check cart is not empty
   ↓
Check stock
   ↓
Calculate total
   ↓
Decrease product stock
   ↓
Delete cart
   ↓
Return total
```

Example response:

``` json
{
  "message": "Order placed successfully",
  "total": 2998.0
}
```

------------------------------------------------------------------------

# 7. MCP Server

MCP server runs on:

``` text
http://127.0.0.1:8001/mcp
```

The MCP server exposes shopping operations as tools.

## MCP tools

### 1. get_products

Purpose:

``` text
Get all available products.
```

### 2. get_cart

Purpose:

``` text
Get current shopping cart contents.
```

### 3. add_to_cart

Arguments:

``` json
{
  "product_id": 11,
  "quantity": 2
}
```

Purpose:

``` text
Add a product to the shopping cart.
```

### 4. checkout

Arguments:

``` text
No arguments
```

Purpose:

``` text
Checkout the current cart.
```

------------------------------------------------------------------------

# 8. Why MCP Is Used

Without MCP, the AI would need custom application-specific integration
for every operation.

With MCP, shopping operations are exposed as standard tools:

``` text
get_products
get_cart
add_to_cart
checkout
```

The AI can decide which tool is required based on the user's request.

For example:

``` text
"Show me available products"
        ↓
get_products
```

``` text
"What's in my cart?"
        ↓
get_cart
```

``` text
"Add 2 Wireless Mouse to my cart"
        ↓
add_to_cart
```

``` text
"Checkout my cart"
        ↓
checkout
```

This is the main MCP concept demonstrated by the project.

------------------------------------------------------------------------

# 9. Groq AI Integration

The AI assistant is implemented in:

``` text
backend/app/ai/assistant.py
```

The model used is:

``` text
openai/gpt-oss-120b
```

The Groq API key is stored in `.env`.

Example:

``` env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

The API key should never be placed in frontend JavaScript or committed
to GitHub.

------------------------------------------------------------------------

# 10. AI Tool Calling

The AI has access to the MCP tools through tool definitions.

The process is:

``` text
User message
     ↓
Groq
     ↓
Does the request need real shopping data?
     ↓
Yes
     ↓
Groq requests an MCP tool
     ↓
FastMCP Client executes the tool
     ↓
MCP Server
     ↓
MySQL
     ↓
Tool result
     ↓
Groq receives tool result
     ↓
Final answer
```

The system prompt also tells the AI:

-   Use MCP tools when real shopping information is required
-   Never invent product names
-   Never invent prices
-   Never invent stock
-   Never invent cart contents
-   Use `get_products` if a product ID is unknown
-   Understand English, Hindi and Hinglish
-   Give short and friendly answers

------------------------------------------------------------------------

# 11. Frontend

The frontend is a single shopping page.

Main sections:

``` text
Products
   ↓
Add to Cart
   ↓
Cart
   ↓
Checkout

AI Shopping Assistant
   ↓
Ask questions
   ↓
Get answers from Groq + MCP
```

The frontend communicates with FastAPI using JavaScript `fetch()`.

Example:

``` javascript
fetch("http://127.0.0.1:8000/products/")
```

AI chat uses:

``` javascript
fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        message: message
    })
})
```

------------------------------------------------------------------------

# 12. AI Chat API

FastAPI exposes:

``` http
POST /chat
```

Request:

``` json
{
  "message": "What is the price of MacBook Pro?"
}
```

Response:

``` json
{
  "reply": "The MacBook Pro is priced at ₹129,999."
}
```

------------------------------------------------------------------------

# 13. Logging

Logging is configured in:

``` text
backend/app/logging_config.py
```

Log file:

``` text
logs/app.log
```

Important events are logged, for example:

``` text
Fetching products
Database connection successful
Products fetched successfully
AI requested MCP tool
Calling MCP tool
MCP tool result
AI response generated successfully
```

Logging helped a lot during debugging because it showed exactly where a
request was failing.

------------------------------------------------------------------------

# 14. Major Problems Faced During Development

## Problem 1: MCP could not connect to MySQL

Initial error:

``` text
1045 (28000): Access denied for user ''@'localhost'
(using password: NO)
```

### Cause

The `.env` file was correct, but the MCP server was running from:

``` text
mcp/server.py
```

while the `.env` file was located in:

``` text
backend/.env
```

Therefore:

``` python
load_dotenv()
```

did not load the expected environment file for the MCP process.

### Fix

The MCP server was changed to load the explicit path:

``` text
project_root/backend/.env
```

After the fix, the debug output showed:

``` text
DB_HOST = localhost
DB_USER = root
DB_NAME = shopping_cart
PASSWORD LOADED = True
```

The MySQL connection then worked.

------------------------------------------------------------------------

# 15. Major Problem 2: MCP Endpoint Returned `null`

The FastAPI MCP endpoint originally used:

``` python
return result.data if hasattr(result, "data") else result
```

The endpoint returned:

``` text
null
```

### Investigation

The raw MCP result showed:

``` text
CallToolResult(
    content=[
        TextContent(
            type='text',
            text='[...]'
        )
    ]
)
```

The actual result was inside:

``` text
result.content[0].text
```

### Fix

The MCP result was extracted from the content and parsed as JSON.

Conceptually:

``` python
text = result.content[0].text
data = json.loads(text)
return data
```

After this, the API returned the actual products.

------------------------------------------------------------------------

# 16. Major Problem 3: Groq AI Could Not Use MCP Result Correctly

The AI initially returned responses such as:

``` text
I wasn't able to retrieve the product details at the moment.
```

### Cause

The MCP result handling inside `assistant.py` was again relying on:

``` python
result.data
```

which could be `None` depending on the FastMCP result.

### Fix

The MCP tool result was handled using:

``` python
result.content[0].text
```

and then:

``` python
json.loads(text)
```

If the content was not JSON, the text itself was returned.

After this fix, the AI correctly answered:

``` text
What is the price of MacBook Pro?
```

with:

``` text
The MacBook Pro is priced at ₹129,999.
```

------------------------------------------------------------------------

# 17. Major Problem 4: Checkout Tool Schema

There was an incorrect checkout tool definition where:

``` python
"required": ["product_id", "quantity"]
```

was accidentally used for checkout.

But checkout does not require any arguments.

The correct definition is:

``` python
"parameters": {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": False
}
```

The `product_id` and `quantity` arguments belong to `add_to_cart`, not
`checkout`.

------------------------------------------------------------------------

# 18. Important Debugging Lesson

The most useful debugging approach in this project was checking each
layer separately.

Instead of assuming the AI was broken, the flow was tested layer by
layer:

``` text
1. MySQL
   ↓
2. MCP Server
   ↓
3. MCP Client
   ↓
4. FastAPI MCP endpoint
   ↓
5. Groq tool calling
   ↓
6. Frontend AI chat
```

This made it possible to identify the actual problem at each stage.

------------------------------------------------------------------------

# 19. Testing Performed

The following AI tests were successfully completed.

## Product listing

Input:

``` text
Show me available products
```

The AI returned the actual products from MySQL.

## Product information

Input:

``` text
What is the price of MacBook Pro?
```

Response:

``` text
MacBook Pro is priced at ₹129,999.
```

## Add to cart

Input:

``` text
Add 1 Wireless Mouse to my cart
```

The item was added to MySQL cart.

## Cart verification

Input:

``` text
What's in my cart?
```

The AI returned the actual cart contents.

## Checkout

Input:

``` text
Checkout my cart
```

The checkout successfully updated stock and cleared the cart.

This confirms the complete AI → MCP → MySQL workflow.

------------------------------------------------------------------------

# 20. Running the Project

## Step 1: Start MySQL

Make sure MySQL is running.

The database:

``` text
shopping_cart
```

must already exist.

------------------------------------------------------------------------

## Step 2: Start MCP Server

Open Terminal 1:

``` powershell
cd C:\Users\ss\Desktop\Shopping_Cart_mcp_server\mcp
python server.py
```

MCP server:

``` text
http://127.0.0.1:8001/mcp
```

------------------------------------------------------------------------

## Step 3: Start FastAPI

Open Terminal 2:

``` powershell
cd C:\Users\ss\Desktop\Shopping_Cart_mcp_server\backend
uvicorn app.main:app --reload
```

FastAPI:

``` text
http://127.0.0.1:8000
```

------------------------------------------------------------------------

## Step 4: Open Frontend

Open:

``` text
frontend/index.html
```

in the browser.

The shopping cart and AI assistant can then be used.

------------------------------------------------------------------------

# 21. Environment Variables

The backend `.env` contains:

``` env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=shopping_cart
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Never commit the real `.env` file.

`.gitignore` should contain:

``` text
.env
```

------------------------------------------------------------------------

# 22. Important Security Point

API keys and passwords are secrets.

Do not:

-   Put `GROQ_API_KEY` in frontend JavaScript
-   Commit `.env` to GitHub
-   Share the real API key
-   Hardcode the MySQL password in source code

Use environment variables instead.

------------------------------------------------------------------------

# 23. Current Project Flow in Simple Words

A simple explanation for presentation:

> This project is a shopping cart application connected to MySQL.
> FastAPI provides the REST APIs for products, cart and checkout. A
> FastMCP server exposes shopping operations as MCP tools. The Groq AI
> assistant uses these MCP tools when the user asks questions that
> require real shopping data. The MCP server performs the requested
> operation using MySQL and sends the result back to the AI. The AI then
> gives a natural-language response to the user.

------------------------------------------------------------------------

# 24. Example Complete Interaction

User:

``` text
Show me available products
```

System:

``` text
Frontend
→ FastAPI
→ Groq
→ get_products
→ MCP Server
→ MySQL
→ Groq
→ Frontend
```

User:

``` text
Add 2 Wireless Mouse to my cart
```

System:

``` text
Frontend
→ FastAPI /chat
→ Groq
→ add_to_cart
→ MCP Server
→ MySQL
→ Groq
→ Frontend
```

User:

``` text
What's in my cart?
```

System:

``` text
Frontend
→ Groq
→ get_cart
→ MCP
→ MySQL
→ Groq
→ Frontend
```

User:

``` text
Checkout my cart
```

System:

``` text
Frontend
→ Groq
→ checkout
→ MCP
→ MySQL
→ Stock updated
→ Cart cleared
→ Groq
→ Frontend
```

------------------------------------------------------------------------

# 25. Project Status

Current core implementation:

``` text
Frontend                  ✅
FastAPI                   ✅
MySQL                     ✅
Products API              ✅
Cart API                  ✅
Checkout API              ✅
MCP Server                ✅
MCP Client                ✅
MCP Tools                 ✅
Groq LLM                  ✅
AI Tool Calling           ✅
AI Product Queries        ✅
AI Cart Queries           ✅
AI Add-to-Cart            ✅
AI Checkout               ✅
Logging                   ✅
```

The core shopping + database + MCP + AI architecture is working
end-to-end.

------------------------------------------------------------------------

# 26. Conclusion

This project demonstrates how a traditional shopping cart application
can be extended with an AI assistant using MCP.

The important architecture is:

``` text
Frontend
   ↓
FastAPI
   ↓
Groq
   ↓
MCP Client
   ↓
MCP Server
   ↓
MCP Tools
   ↓
MySQL
```

The main benefit of MCP in this project is that shopping operations are
exposed as clear tools that an AI model can call when required.

The project also demonstrates practical debugging of a multi-layer
application by checking database connectivity, MCP communication, tool
results, AI tool calling and frontend responses separately.
