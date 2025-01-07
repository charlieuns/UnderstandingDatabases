# Query: Customers search for the most expensive product within a specific price range among a fixed category of goods, displaying its current inventory status. If sufficient inventory is available, the product is added to the shopping cart. 
# The shopping cart is updated with the product details, quantity, and total price, while the system marks the historical purchase record. Finally, the product inventory is updated to reflect the purchase.

from pymongo import MongoClient
from typing import Dict, Optional
import pandas as pd
from tabulate import tabulate  # pip install tabulate

# Connect to MongoDB
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']

# Collections
customers_collection = db['Customers']
products_collection = db['Products']
past_orders_collection = db['PastOrders']
inventory_collection = db['Inventory']

# Query parameters
customer_id = 6
product_type = "book"
price_range = (10, 200)
quantity_to_buy = 5

def find_most_expensive_book() -> Optional[Dict]:
    """Find the most expensive book within the price range."""
    try:
        book = products_collection.find_one(
            {'product_category': product_type, 'price': {'$gte': price_range[0], '$lte': price_range[1]}},
            sort=[('price', -1)]
        )
        if not book:
            print("\nNo books found in the specified category and price range.")
            return None

        print("\n=== Most Expensive Book Found ===")
        print(tabulate(pd.DataFrame([book]), headers="keys", tablefmt="grid"))
        return book
    except Exception as e:
        print(f"Error finding book: {str(e)}")
        return None

def check_purchase_history(customer_id: int, product_id: int) -> bool:
    """Check if the customer has purchased the book before."""
    try:
        purchased = past_orders_collection.find_one({
            'customer_ID': customer_id,
            'products.product_ID': product_id
        }) is not None
        print(f"\n=== Purchase History ===\nPreviously Purchased: {'Yes' if purchased else 'No'}")
        return purchased
    except Exception as e:
        print(f"Error checking purchase history: {str(e)}")
        return False

def check_inventory(product_id: int, quantity: int) -> Dict:
    """Check if there is enough stock."""
    inventory_item = inventory_collection.find_one({'product_ID': product_id})
    if not inventory_item:
        return {'success': False, 'message': 'Product does not exist'}

    available_quantity = inventory_item.get('inventory', 0)
    success = available_quantity >= quantity
    message = "Sufficient stock available." if success else f"Only {available_quantity} available, cannot fulfill order."

    print("\n=== Inventory Check ===")
    inventory_df = pd.DataFrame([{
        "Product ID": product_id,
        "Available Quantity": available_quantity,
        "Requested Quantity": quantity,
        "Success": "Yes" if success else "No",
        "Message": message
    }])
    print(tabulate(inventory_df, headers="keys", tablefmt="grid"))
    return {'success': success, 'message': message}

def update_cart(customer_id: int, book: Dict, quantity: int) -> Dict:
    """Update the customer's cart with the selected book."""
    try:
        item_total = book['price'] * quantity
        customer = customers_collection.find_one({'customer_ID': customer_id})
        if not customer:
            return {'success': False, 'message': f'Customer {customer_id} does not exist.'}

        cart = customer.get('cart', {'products': [], 'cart_total': 0})
        for product in cart['products']:
            if product['product_ID'] == book['product_ID']:
                product['quantity'] += quantity
                break
        else:
            cart['products'].append({'product_ID': book['product_ID'], 'quantity': quantity})

        cart['cart_total'] += item_total
        customers_collection.update_one({'customer_ID': customer_id}, {'$set': {'cart': cart}})

        print("\n=== Updated Cart ===")
        cart_df = pd.DataFrame(cart['products'])
        cart_df['Total Price'] = cart_df['quantity'] * book['price']
        print(tabulate(cart_df, headers="keys", tablefmt="grid"))
        return {'success': True, 'cart_details': cart}
    except Exception as e:
        return {'success': False, 'message': f'Failed to update cart: {str(e)}'}

def update_inventory(product_id: int, quantity: int) -> None:
    """Reduce the inventory of the selected product."""
    inventory_collection.update_one({'product_ID': product_id}, {'$inc': {'inventory': -quantity}})
    print(f"\n=== Updated Inventory ===\nReduced inventory for Product ID {product_id} by {quantity}")

def purchase_book(customer_id: int, quantity: int) -> None:
    """Main function to purchase a book."""
    try:
        book = find_most_expensive_book()
        if not book:
            return

        check_purchase_history(customer_id, book['product_ID'])

        inventory_check = check_inventory(book['product_ID'], quantity)
        if not inventory_check['success']:
            print(f"\nOperation failed: {inventory_check['message']}")
            return

        cart_update = update_cart(customer_id, book, quantity)
        if not cart_update['success']:
            print(f"\nOperation failed: {cart_update['message']}")
            return

        update_inventory(book['product_ID'], quantity)

        print("\n=== Purchase Summary ===")
        summary = {
            'Book Name': book['name'],
            'Price per Unit': book['price'],
            'Quantity Purchased': quantity,
            'Total Cost': book['price'] * quantity,
            'Updated Cart Total': cart_update['cart_details']['cart_total']
        }
        print(tabulate(pd.DataFrame([summary]), headers="keys", tablefmt="grid"))
    except Exception as e:
        print(f"Error during purchase: {str(e)}")

# Execute purchase
purchase_book(customer_id, quantity_to_buy)


# Execute purchase and display the result
purchase_book(customer_id, quantity_to_buy)

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
