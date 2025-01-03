# Query: Customer checks the current shopping cart contents and remove the lowest-priced item. And the total price of the cart is updated accordingly. A new order is then created based on the remaining items in the shopping cart, and payment is processed. 
# The order record is updated in the database, and the customer document is modified to reflect the new order and the cleared shopping cart. Additionally, inventory levels for the purchased items are adjusted to reflect the transaction.
from pymongo import MongoClient
from typing import Dict, Optional
from datetime import datetime
import random
import pandas as pd

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['DatabaseName']

# Collections
customers_collection = db['Customers']
products_collection = db['Products']
past_orders_collection = db['PastOrders']
inventory_collection = db['Inventory']
partners_collection = db['Partners']

# Customer ID
customer_id = 5

def get_cart_contents(customer_id: int):
    """Retrieve the cart contents for a given customer ID."""
    customer = customers_collection.find_one({'customer_ID': customer_id})
    if not customer:
        return None, "Customer not found."
    
    cart = customer.get('cart', {})
    return cart, "Cart retrieved successfully."

def remove_lowest_priced_item(cart: dict):
    if not cart.get('products'):
        return None, "Cart is empty."

    # Fetch product prices from the Products collection
    for product in cart['products']:
        product_data = products_collection.find_one({'product_ID': product['product_ID']}, {'price': 1})
        product['price'] = product_data['price'] if product_data else 0  # Set price to 0 if product not found

    # Find the lowest-priced product
    lowest_priced_product = min(
        cart['products'], 
        key=lambda x: x['quantity'] * x['price']  # Sort by total price
    )
    
    # Remove the lowest-priced product
    cart['products'].remove(lowest_priced_product)
    
    # Update the cart total
    cart['cart_total'] = sum(
        product['quantity'] * product['price'] for product in cart['products']
    )
    
    return cart, f"Removed product: {lowest_priced_product['product_ID']}."

def create_order(customer_id: int, cart: dict):
    """Create a new order for the customer."""
    if not cart.get('products'):
        return None, "Cannot create order: Cart is empty."
    
    # Randomly assign a delivery person from the Partners set
    partner = partners_collection.aggregate([{"$sample": {"size": 1}}])
    partner_id = list(partner)[0]['partner_ID'] if partner else None

    # Generate random destination from customer addresses
    customer = customers_collection.find_one({'customer_ID': customer_id})
    addresses = customer.get("addresses", [])
    order_destination = random.choice(addresses) if addresses else "Default Address"

    # Create the order document
    order = {
        "order_ID": db['PastOrders'].count_documents({}) + 1,  # Generate new order ID
        "customer_ID": customer_id,
        "order_total": cart['cart_total'],
        "order_status": "Paid",
        "order_placed": datetime.now(),
        "order_delivered": None,  # Update after delivery
        "partner_assigned": partner_id,
        "order_destination": order_destination,
        "products": cart['products']
    }

    # Insert the order into the PastOrders collection
    past_orders_collection.insert_one(order)
    
    return order, "Order created successfully."

def update_inventory(order):
    """Update inventory quantities based on the order."""
    for product in order['products']:
        inventory_collection.update_one(
            {'product_ID': product['product_ID']},
            {'$inc': {'inventory': -product['quantity']}}
        )

def update_customer_document(customer_id: int, order: dict):
    """Update the customer's document with the new order."""
    update_result = customers_collection.update_one(
        {'customer_ID': customer_id},
        {
            '$set': {'cart': {"products": [], "cart_total": 0}},  # Empty the cart
            '$push': {'current_orders': {
                "order_ID": order['order_ID'],
                "order_total": order['order_total'],
                "order_status": order['order_status'],
                "partner_assigned": order['partner_assigned'],
                "order_placed": order['order_placed'],
                "order_destination": order['order_destination'],
                "products": order['products']
            }}  # Add the order details to current orders
        }
    )
    if update_result.modified_count > 0:
        return True, "Customer document updated successfully."
    return False, "Failed to update customer document."

def process_cart_and_create_order(customer_id: int):
    """Process the cart and create an order for the customer."""
    # Step 1: Retrieve cart contents
    cart, message = get_cart_contents(customer_id)
    if not cart:
        return {"success": False, "message": message}

    print(f"Step 1 - Cart contents: {cart}")

    # Step 2: Remove the lowest-priced item
    cart, message = remove_lowest_priced_item(cart)
    print(f"Step 2 - {message}")

    # Step 3: Create a new order
    order, message = create_order(customer_id, cart)
    if not order:
        return {"success": False, "message": message}
    
    print(f"Step 3 - {message}. Order details: {order}")

    # Step 4: Update inventory
    update_inventory(order)
    print("Step 4 - Inventory updated.")

    # Step 5: Update customer document
    success, message = update_customer_document(customer_id, order)
    print(f"Step 5 - {message}")
    
    # Return the final results
    result_data = {
        'Order ID': order['order_ID'],
        'Customer ID': order['customer_ID'],
        'Order Total': order['order_total'],
        'Order Status': order['order_status'],
        'Partner Assigned': order['partner_assigned'],
        'Products': order['products']
    }
    return pd.DataFrame([result_data])

# Execute the query and display the result
result_df = process_cart_and_create_order(customer_id)

# Display the result as a table
print(result_df)

# Query Description:
# This query processes a customer's shopping cart by performing several operations in sequence:

# Retrieve Shopping Cart Contents:
# The system retrieves the current contents of the shopping cart for a specific customer, including the list of products, their quantities, and the total price.

# Remove the Lowest-Priced Item:
# Among the items in the shopping cart, the product with the lowest total value (quantity × price) is identified and removed.

# Update Shopping Cart Total:
# After removing the lowest-priced item, the total price of the shopping cart is recalculated and updated in the customer's record.

# Create a New Order:
# The remaining items in the shopping cart are used to create a new order. The order includes details such as the total price, the list of products, and the quantities ordered.
# A delivery partner is randomly assigned to the order, and the payment status is marked as "Paid."

# Record the Order in the Database:
# The newly created order is added to the PastOrders collection in MongoDB, maintaining a record of the transaction.

# Update Customer Document:
# The customer's document in the database is updated to reflect the transaction: The shopping cart is cleared. The new order is linked to the customer's list of orders.

# Adjust Inventory Levels:
# For each product in the new order, the system updates the inventory records to reduce the available stock by the quantity purchased.

# This query ensures that the customer's shopping cart, orders, and inventory levels are accurately updated in the database, providing a consistent and reliable transaction workflow.