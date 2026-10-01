const API_URL = "http://127.0.0.1:8000";


// =====================================================
// PAGE LOAD
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("NovaCart JS loaded successfully");

    loadProducts();
    loadCart();

});


// =====================================================
// LOAD PRODUCTS
// =====================================================

async function loadProducts() {

    const container =
        document.getElementById("products-container");

    if (!container) {
        console.error(
            "ERROR: products-container not found in HTML"
        );
        return;
    }

    try {

        container.innerHTML = `
            <div class="loading">
                Loading products...
            </div>
        `;

        const response = await fetch(
            API_URL + "/products/",
            {
                method: "GET"
            }
        );

        if (!response.ok) {

            throw new Error(
                "Products API returned " +
                response.status
            );
        }

        const products = await response.json();

        console.log("Products:", products);

        if (!Array.isArray(products)) {

            throw new Error(
                "Invalid products response"
            );
        }

        if (products.length === 0) {

            container.innerHTML = `
                <div class="loading">
                    No products found.
                </div>
            `;

            return;
        }

        renderProducts(products);

    } catch (error) {

        console.error(
            "Product loading failed:",
            error
        );

        container.innerHTML = `
            <div class="loading">
                ❌ Unable to load products.
                <br>
                <small>${error.message}</small>
            </div>
        `;
    }
}


// =====================================================
// RENDER PRODUCTS
// =====================================================

function renderProducts(products) {

    const container =
        document.getElementById("products-container");

    container.innerHTML = "";

    products.forEach(function (product) {

        const card =
            document.createElement("div");

        card.className = "product-card";


        const name =
            product.name || "Product";


        const category =
            product.category || "General";


        const price =
            Number(product.price || 0)
                .toLocaleString("en-IN");


        const stock =
            Number(product.stock || 0);


        card.innerHTML = `

            <div class="product-icon">
                ${getProductIcon(name)}
            </div>

            <h3>
                ${escapeHTML(name)}
            </h3>

            <div class="product-category">
                ${escapeHTML(category)}
            </div>

            <div class="product-bottom">

                <div class="product-price">
                    ₹${price}
                </div>

                <button
                    class="add-button"
                    type="button"
                    onclick="addToCart(${Number(product.id)})"
                    ${stock <= 0 ? "disabled" : ""}
                >
                    ${
                        stock <= 0
                            ? "Out of Stock"
                            : "Add to Cart"
                    }
                </button>

            </div>

        `;

        container.appendChild(card);

    });

    console.log(
        products.length +
        " products displayed"
    );
}


// =====================================================
// PRODUCT ICON
// =====================================================

function getProductIcon(name) {

    const value =
        String(name).toLowerCase();


    if (value.includes("macbook")) {
        return "💻";
    }

    if (value.includes("laptop")) {
        return "💻";
    }

    if (value.includes("mouse")) {
        return "🖱️";
    }

    if (value.includes("keyboard")) {
        return "⌨️";
    }

    if (value.includes("phone")) {
        return "📱";
    }

    if (value.includes("headphone")) {
        return "🎧";
    }

    if (value.includes("watch")) {
        return "⌚";
    }

    if (value.includes("camera")) {
        return "📷";
    }

    return "🛍️";
}


// =====================================================
// ADD TO CART
// =====================================================

async function addToCart(productId) {

    try {

        const response = await fetch(
            API_URL + "/cart/add",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    product_id: Number(productId),
                    quantity: 1
                })
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to add product"
            );
        }


        console.log(
            "Added to cart:",
            data
        );


        await loadCart();


        showMessage(
            "✓ Product added to cart!",
            "success"
        );


    } catch (error) {

        console.error(
            "Add to cart error:",
            error
        );


        showMessage(
            "❌ " + error.message,
            "error"
        );
    }
}


// =====================================================
// LOAD CART
// =====================================================

async function loadCart() {

    try {

        const response =
            await fetch(
                API_URL + "/cart/",
                {
                    method: "GET"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Cart API returned " +
                response.status
            );
        }


        const cart =
            await response.json();


        console.log(
            "Cart:",
            cart
        );


        renderCart(cart);


    } catch (error) {

        console.error(
            "Cart loading error:",
            error
        );
    }
}


// =====================================================
// RENDER CART
// =====================================================

function renderCart(cart) {

    const container =
        document.getElementById("cart-items");


    if (!container) {
        return;
    }


    if (
        !Array.isArray(cart) ||
        cart.length === 0
    ) {

        container.innerHTML = `

            <div class="empty-cart">

                <div class="empty-icon">
                    🛒
                </div>

                <h3>
                    Your cart is empty
                </h3>

                <p>
                    Add products to your cart.
                </p>

                <a
                    href="#products"
                    class="continue-shopping"
                >
                    Start Shopping →
                </a>

            </div>

        `;


        updateCartCount(0);
        updateSummary(0);

        return;
    }


    container.innerHTML = "";


    cart.forEach(function (item) {

        const cartItem =
            document.createElement("div");


        cartItem.className =
            "cart-item";


        const name =
            item.name || "Product";


        const price =
            Number(item.price || 0)
                .toLocaleString("en-IN");


        const subtotal =
            Number(item.subtotal || 0)
                .toLocaleString("en-IN");


        const quantity =
            Number(item.quantity || 1);


        cartItem.innerHTML = `

            <div class="cart-item-info">

                <div class="cart-item-icon">
                    ${getProductIcon(name)}
                </div>

                <div>

                    <h3>
                        ${escapeHTML(name)}
                    </h3>

                    <div class="cart-item-price">
                        ₹${price}
                    </div>

                </div>

            </div>


            <div class="quantity-controls">

                <button
                    type="button"
                    onclick="
                        changeQuantity(
                            ${Number(item.id)},
                            ${Number(item.product_id)},
                            ${quantity - 1}
                        )
                    "
                >
                    −
                </button>


                <strong>
                    ${quantity}
                </strong>


                <button
                    type="button"
                    onclick="
                        changeQuantity(
                            ${Number(item.id)},
                            ${Number(item.product_id)},
                            ${quantity + 1}
                        )
                    "
                >
                    +
                </button>

            </div>


            <strong>
                ₹${subtotal}
            </strong>


            <button
                class="remove-button"
                type="button"
                onclick="
                    removeFromCart(${Number(item.id)})
                "
            >
                Remove
            </button>

        `;


        container.appendChild(cartItem);

    });


    const totalItems =
        cart.reduce(
            function (total, item) {

                return total +
                    Number(item.quantity || 0);

            },
            0
        );


    const totalPrice =
        cart.reduce(
            function (total, item) {

                return total +
                    Number(item.subtotal || 0);

            },
            0
        );


    updateCartCount(totalItems);

    updateSummary(totalPrice);
}


// =====================================================
// CHANGE QUANTITY
// =====================================================

async function changeQuantity(
    cartId,
    productId,
    newQuantity
) {

    if (newQuantity <= 0) {

        await removeFromCart(cartId);

        return;
    }


    try {

        /*
         Backend currently does not have
         update quantity endpoint.

         Therefore:

         DELETE old cart item
         +
         ADD same product with new quantity
        */


        const deleteResponse =
            await fetch(
                API_URL +
                "/cart/" +
                Number(cartId),
                {
                    method: "DELETE"
                }
            );


        if (!deleteResponse.ok) {

            throw new Error(
                "Unable to update cart"
            );
        }


        const addResponse =
            await fetch(
                API_URL + "/cart/add",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        product_id:
                            Number(productId),

                        quantity:
                            Number(newQuantity)
                    })
                }
            );


        const data =
            await addResponse.json();


        if (!addResponse.ok) {

            throw new Error(
                data.detail ||
                "Unable to update quantity"
            );
        }


        await loadCart();


    } catch (error) {

        console.error(
            "Quantity update error:",
            error
        );


        showMessage(
            "❌ " + error.message,
            "error"
        );


        await loadCart();
    }
}


// =====================================================
// REMOVE FROM CART
// =====================================================

async function removeFromCart(cartId) {

    try {

        const response =
            await fetch(
                API_URL +
                "/cart/" +
                Number(cartId),
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to remove item"
            );
        }


        await loadCart();


        showMessage(
            "✓ Item removed from cart",
            "success"
        );


    } catch (error) {

        console.error(
            "Remove cart error:",
            error
        );


        showMessage(
            "❌ " + error.message,
            "error"
        );
    }
}


// =====================================================
// CART COUNT
// =====================================================

function updateCartCount(count) {

    const cartCount =
        document.getElementById(
            "cart-count"
        );


    const itemsCount =
        document.getElementById(
            "cart-items-count"
        );


    if (cartCount) {

        cartCount.textContent =
            String(count);
    }


    if (itemsCount) {

        itemsCount.textContent =
            count +
            (count === 1
                ? " item"
                : " items");
    }
}


// =====================================================
// ORDER SUMMARY
// =====================================================

function updateSummary(total) {

    const formatted =
        Number(total || 0)
            .toLocaleString("en-IN");


    const subtotal =
        document.getElementById(
            "subtotal"
        );


    const cartTotal =
        document.getElementById(
            "cart-total"
        );


    if (subtotal) {

        subtotal.textContent =
            "₹" + formatted;
    }


    if (cartTotal) {

        cartTotal.textContent =
            "₹" + formatted;
    }
}


// =====================================================
// CHECKOUT
// =====================================================

async function checkout() {

    const messageBox =
        document.getElementById(
            "checkout-message"
        );


    try {

        const response =
            await fetch(
                API_URL + "/checkout/",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Checkout failed"
            );
        }


        if (messageBox) {

            messageBox.className =
                "checkout-message success";


            messageBox.textContent =
                "✓ Order placed successfully! " +
                "Total: ₹" +
                Number(data.total || 0)
                    .toLocaleString("en-IN");
        }


        await loadCart();


        setTimeout(function () {

            if (messageBox) {

                messageBox.className =
                    "checkout-message";

                messageBox.textContent = "";
            }

        }, 5000);


    } catch (error) {

        console.error(
            "Checkout error:",
            error
        );


        if (messageBox) {

            messageBox.className =
                "checkout-message error";


            messageBox.textContent =
                "❌ " + error.message;
        }
    }
}


// =====================================================
// MESSAGE
// =====================================================

function showMessage(
    message,
    type
) {

    const messageBox =
        document.getElementById(
            "checkout-message"
        );


    if (!messageBox) {
        return;
    }


    messageBox.className =
        "checkout-message " + type;


    messageBox.textContent =
        message;


    setTimeout(function () {

        messageBox.className =
            "checkout-message";

        messageBox.textContent = "";

    }, 4000);
}


// =====================================================
// SCROLL TO CART
// =====================================================

function scrollToCart() {

    const cart =
        document.getElementById("cart");


    if (cart) {

        cart.scrollIntoView({
            behavior: "smooth"
        });
    }
}


// =====================================================
// HTML SAFETY
// =====================================================

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}