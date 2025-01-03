# Query: Customers search for the most expensive product within a specific price range among a fixed category of goods, displaying its current inventory status. If sufficient inventory is available, the product is added to the shopping cart. 
# The shopping cart is updated with the product details, quantity, and total price, while the system marks the historical purchase record. Finally, the product inventory is updated to reflect the purchase.

from pymongo import MongoClient, ASCENDING
from datetime import datetime
from typing import Dict, Optional
import pandas as pd

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['DatabaseName']

# Collections
customers_collection = db['Customers']
products_collection = db['Products']
past_orders_collection = db['PastOrders']
inventory_collection = db['Inventory']

# Customer ID and product query parameters
customer_id = 5
product_type = "book"
price_range = (150, 200)
quantity_to_buy = 5

def find_most_expensive_book() -> Optional[Dict]:
    """Find the most expensive book within the price range."""
    books = products_collection.find(
        {'product_category': product_type, 'price': {'$gte': price_range[0], '$lte': price_range[1]}},
        sort=[('price', -1)]
        ).limit(1)
    return books[0] if books else None

def check_purchase_history(customer_id: int, product_id: int) -> bool:
    """Check if the customer has purchased the book before."""
    purchase = past_orders_collection.find_one({
        'customer_ID': customer_id,
        'products.product_ID': product_id
    })
    return purchase is not None

def check_inventory(product_id: int, quantity: int) -> Dict:
    """Check if there is enough stock."""
    inventory_item = inventory_collection.find_one({'product_ID': product_id})
    
    if not inventory_item:
        return {
            'success': False,
            'message': 'Product does not exist',
            'available': 0
        }

    available_quantity = inventory_item.get('inventory', 0)
    
    # Inventory Tips
    if available_quantity < quantity:
        if available_quantity < 3:
            return {
                'success': False,
                'message': f'Only {available_quantity} available, cannot fulfill order.',
                'available': available_quantity
            }
        else:
            return {
                'success': False,
                'message': 'Insufficient stock, cannot fulfill order.',
                'available': available_quantity
            }
    
    # there is enough inventory
    if available_quantity < 3:
        return {
            'success': True,
            'message': f'Sufficient stock available. Only {available_quantity} left!',
            'available': available_quantity
        }
    else:
        return {
            'success': True,
            'message': 'Sufficient stock available.',
            'available': None  
        }

def update_cart(customer_id: int, book: Dict, quantity: int) -> Dict:
    """Update the customer's cart with the selected book."""
    try:
        item_total = book['price'] * quantity
        customer = customers_collection.find_one({'customer_ID': customer_id})
        
        if not customer:
            return {'success': False, 'message': f'Customer {customer_id} does not exist.'}

        cart = customer.get('cart', {'products': [], 'cart_total': 0})
        
        # Check if the product already exists in the cart
        product_found = False
        for product in cart['products']:
            if product['product_ID'] == book['product_ID']:
                product['quantity'] += quantity
                product_found = True
                break

        if not product_found:
            cart['products'].append({
                'product_ID': book['product_ID'],
                'quantity': quantity
            })

        cart['cart_total'] += item_total

        # Print before updating
        print(f"Updating cart for customer {customer_id}: {cart}")

        # Update the customer's cart
        result = customers_collection.update_one(
            {'customer_ID': customer_id},
            {'$set': {'cart': cart}}
        )

        # Print the update result
        print(f"Cart Update Result: {result.raw_result}")

        return {
            'success': True,
            'cart_details': cart
        }

    except Exception as e:
        return {'success': False, 'message': f'Failed to update cart: {str(e)}'}

def update_inventory(product_id: int, quantity: int) -> None:
    """Reduce the inventory of the selected product."""
    print(f"Updating inventory for product {product_id}, reducing by {quantity}")
    result = inventory_collection.update_one(
        {'product_ID': product_id},
        {'$inc': {'inventory': -quantity}}
    )
    print(f"Inventory Update Result: {result.raw_result}")


def purchase_book(customer_id: int, quantity: int) -> pd.DataFrame:
    """Main function to purchase a book and return results as a DataFrame."""
    try:
        # 1. Find the most expensive book
        book = find_most_expensive_book()
        if not book:
            return pd.DataFrame([{'Result': 'No matching books found.'}])

        # 2. Check purchase history
        has_purchased = check_purchase_history(customer_id, book['product_ID'])

        # 3. Check inventory
        inventory_check = check_inventory(book['product_ID'], quantity)
        if not inventory_check['success']:
            return pd.DataFrame([{'Result': inventory_check['message']}])

        # 4. Update cart
        cart_update = update_cart(customer_id, book, quantity)
        if not cart_update['success']:
            return pd.DataFrame([{'Result': cart_update['message']}])

        # 5. Update inventory
        update_inventory(book['product_ID'], quantity)

        # Construct the result as a DataFrame
        result_data = {
            'Book Name': [book['name']],
            'Price per Unit': [book['price']],
            'Quantity Purchased': [quantity],
            'Total Cost': [book['price'] * quantity],
            'Previously Purchased': ['Yes' if has_purchased else 'No'],
            'Updated Cart Total': [cart_update['cart_details']['cart_total']]
        }
        return pd.DataFrame(result_data)

    except Exception as e:
        return pd.DataFrame([{'Result': f'Operation failed: {str(e)}'}])

# Execute purchase and display the result
result_df = purchase_book(customer_id, quantity_to_buy)

# Display the result in tabular format
print(result_df)

# Description of the Query
# The query implements the following process for a customer to find and purchase a product:
# Finding the Product:
# The customer searches for the most expensive product of a specific type (book) within a given price range (150-200) from the Products collection. The product with the highest price in this range is identified and selected.

# Checking Current Inventory:
# The current inventory of the selected product is retrieved from the Inventory collection. If the stock is less than the requested quantity, the process stops, and the available stock is displayed.
# If the stock is sufficient, the process proceeds to the next step.

# Adding to Cart:
# The selected product is added to the customer’s cart. If the product is already present in the cart, the quantity is updated.
# The cart's total price is recalculated based on the product price and quantity. The updated cart information is stored in the Customers collection.

# Marking Purchase History:
# The system checks the PastOrders collection to mark whether the customer has purchased this product before. This information is included in the response for analytics and historical tracking.

# Updating Inventory:
# The Inventory collection is updated to reduce the stock of the selected product by the purchased quantity. Real-time inventory synchronization ensures accuracy for future queries.
# Result:
# If successful, the system returns details of the selected product, the updated cart (including products, quantity, and total price), and a flag indicating if the product was previously purchased.
# If the process fails due to insufficient stock or other reasons, a detailed error message is returned, such as "Insufficient stock" or "No matching product found."