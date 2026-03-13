Project: Order Analytics Service
Goal:
Build a small Python service that analyzes e-commerce order data and provides
useful business insights.
Core Features:

1. Load Orders
The system should load order data from a CSV file.
Fields:
order_id
customer_name
product
category
price
quantity
order_date
2. Revenue Calculation
The system should calculate:
- Total revenue
- Revenue per product
- Revenue per category

3. Top Customers
Return the top N customers by total spending.

4. Monthly Revenue
Aggregate revenue by month.
5. Simple API Functions

Required functions:
load_orders(file_path)
calculate_total_revenue(orders)

revenue_by_product(orders)
revenue_by_category(orders)
top_customers(orders, n=3)

monthly_revenue(orders)
6. Requirements

- Written in Python
- Use pandas
- Code must be modular
- Should handle missing data gracefully
- Include docstrings
- Follow PEP8 style
