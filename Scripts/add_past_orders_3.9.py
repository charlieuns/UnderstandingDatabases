from pymongo import MongoClient
import random
from datetime import datetime, timedelta

# Connect to MongoDB
# Connect to MongoDB
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']

# Collections
customers_collection = db['Customers']
products_collection = db['Products']
partners_collection = db['Partners']  
past_orders_collection = db['PastOrders']

# Fetch customer and product IDs
customer_ids = [customer['customer_ID'] for customer in customers_collection.find({}, {"customer_ID": 1})]
product_ids = [product['product_ID'] for product in products_collection.find({}, {"product_ID": 1})]
partner_ids = [partner['partner_ID'] for partner in partners_collection.find({}, {"partner_ID": 1})] 

# Generate past orders for each customer
past_orders = []
order_id = 70  # Unique order ID

for customer_id in customer_ids:
    # Each customer has between 5 and 7 past orders
    num_orders = random.randint(5, 7)
    for _ in range(num_orders):
        # Random partner assignment
        partner_id = random.choice(partner_ids)
        
        # Order details
        num_products = random.randint(1, 5)  # Number of products in the order
        products = []
        order_total = 0

        for _ in range(num_products):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 10)
            
            # Fetch product price from the Products collection
            product = products_collection.find_one({"product_ID": product_id}, {"price": 1})
            price = product['price'] if product else 0
            
            products.append({
                "product_ID": product_id,
                "quantity": quantity
            })
            order_total += price * quantity

        # Random timestamps for order placement and delivery
        order_placed = datetime.now() - timedelta(days=random.randint(1, 365))
        order_delivered = order_placed + timedelta(days=random.randint(1, 5))  # Delivered 1-5 days later

        # Append the past order to the list
        past_orders.append({
            "order_ID": order_id,
            "customer_ID": customer_id,
            "order_total": round(order_total, 2),
            "partner_assigned": partner_id,
            "order_placed": order_placed,
            "order_delivered": order_delivered,
            "products": products
        })
        order_id += 1

# Insert into PastOrders collection
past_orders_collection.insert_many(past_orders)
