git WITH recent_orders AS (
    SELECT order_id, customer_id
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '1 year'
),
customer_spending AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.email,
        SUM(oi.quantity * oi.price_per_unit) AS total_spent
    FROM customers c
    JOIN recent_orders ro ON c.customer_id = ro.customer_id
    JOIN order_items oi ON ro.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name, c.email
),
category_spending AS (
    SELECT
        c.customer_id,
        p.category,
        SUM(oi.quantity * oi.price_per_unit) AS category_total,
        RANK() OVER (
            PARTITION BY c.customer_id
            ORDER BY SUM(oi.quantity * oi.price_per_unit) DESC
        ) AS rnk
    FROM customers c
    JOIN recent_orders ro ON c.customer_id = ro.customer_id
    JOIN order_items oi ON ro.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY c.customer_id, p.category
)
SELECT
    cs.customer_id,
    cs.customer_name,
    cs.email,
    ROUND(cs.total_spent,2) AS total_spent,
    csp.category AS most_purchased_category
FROM customer_spending cs
JOIN category_spending csp
    ON cs.customer_id = csp.customer_id
   AND csp.rnk = 1
ORDER BY cs.total_spent DESC
LIMIT 5;
