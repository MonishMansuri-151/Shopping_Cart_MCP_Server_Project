CREATE DATABASE shopping_cart;

USE shopping_cart;


-- =========================
-- PRODUCTS TABLE
-- =========================

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    category VARCHAR(100) NOT NULL,

    price DECIMAL(10, 2) NOT NULL,

    stock INT NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================
-- CART TABLE
-- =========================

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,

    product_id INT NOT NULL,

    quantity INT NOT NULL DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);