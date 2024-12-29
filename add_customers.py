from pymongo import MongoClient
import random
import string
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://')
db = client['YourDatabaseName']
customers_collection = db['Customers']
products_collection = db['Products']

# Example data for generating customer records
male_names = ["Adam", "Charlie", "Edward", "George", "Jack", "Liam", "Nathan", "Oscar", "Paul", "Sam"]
female_names = ["Beth", "Diana", "Fiona", "Hannah", "Ivy", "Karen", "Mona", "Olivia", "Rachel", "Tina"]
last_initials = [chr(i) for i in range(65, 91)]  # A-Z
uk_cities = ["London", "Manchester", "Birmingham", "Leeds", "Glasgow", "Liverpool", "Bristol", "Sheffield", "Edinburgh", "Cardiff"]
uk_streets = ["High Street", "Station Road", "Church Lane", "Victoria Road", "Park Avenue", "Main Street", "Mill Lane", "The Crescent", "Queensway", "King Street"]
address_types = ["Home", "Work"]

# Helper function to generate UK postcodes
def generate_uk_postcode():
    area = random.choice(string.ascii_uppercase)  # One letter for the area
    district = str(random.randint(1, 99))  # One or two digits for the district
    outward_code = f"{area}{district}"
    sector = str(random.randint(0, 9))  # Single digit
    unit = ''.join(random.choices(string.ascii_uppercase, k=2))  # Two random letters
    inward_code = f"{sector}{unit}"
    return f"{outward_code} {inward_code}"

# Generate a random latitude and longitude for location within the UK
def generate_uk_location():
    latitude = random.uniform(49.3, 58.6)  # UK latitude bounds
    longitude = random.uniform(-8.1, 1.8)  # UK longitude bounds
    return latitude, longitude

# Fetch all product IDs and their prices from the Products collection
product_data = {product["product_ID"]: product["price"] for product in products_collection.find({}, {"product_ID": 1, "price": 1})}
product_ids = list(product_data.keys())

# Fetch all unique product types from the Products collection
product_types = products_collection.distinct("product_type")

# Generate 20 customers
customers = []
order_id = 1
for i in range(20):
    if i < 10:
        first_name = male_names[i]
        gender = "Male"
    else:
        first_name = female_names[i - 10]
        gender = "Female"
    
    last_initial = random.choice(last_initials)
    name = f"{first_name} {last_initial}"
    age = random.randint(18, 70)
    
    # Generate 1 address for each customer
    addresses = [{
        "address_type": random.choice(address_types),
        "house_number": random.randint(1, 999),
        "street": random.choice(uk_streets),
        "city": random.choice(uk_cities),
        "postcode": generate_uk_postcode()  # UK postcode generator
    }]
    
    # Generate latitude and longitude within the UK
    latitude, longitude = generate_uk_location()
    
    # Generate 2-3 current orders for each customer
    current_orders = []
    for _ in range(2):
        products_in_order = [
            {
                "product_ID": random.choice(product_ids),
                "quantity": random.randint(1, 10)
            }
            for _ in range(random.randint(1, 5))  # Each order has 1-5 products
        ]
        
        # Calculate the order total based on product prices and quantities
        order_total = sum(product_data[product["product_ID"]] * product["quantity"] for product in products_in_order)
        
        # Select customer addresses to be the order destination
        order_destination = f"{addresses[0]['house_number']} {addresses[0]['street']}, {addresses[0]['city']}, {addresses[0]['postcode']}"
        
        current_orders.append({
            "order_ID": order_id,
            "order_total": round(order_total, 2),
            "order_status": random.choice(["Pending", "Shipped", "Delivered"]),
            "partner_assigned": random.randint(1, 10),  # Random partner ID
            "order_placed": datetime.now(),  # Current datetime for order placement
            "order_destination": order_destination,
            "products": products_in_order
        })
        order_id += 1
    
    # Generate the cart with product details
    cart_products = [
        {
            "product_ID": random.choice(product_ids),
            "quantity": random.randint(1, 5)
        }
        for _ in range(random.randint(1, 5))
    ]
    cart_total = sum(product_data[product["product_ID"]] * product["quantity"] for product in cart_products)
    
    # Create the customer document
    customers.append({
        "customer_ID": i + 1,
        "name": name,
        "gender": gender,
        "age": age,
        "addresses": addresses,  
        "location": {"latitude": latitude, "longitude": longitude},
        "cart": {"cart_total": round(cart_total, 2), "products": cart_products},
        "current_orders": current_orders,
        "commonly_ordered_categories": random.sample(product_types, k=min(len(product_types), random.randint(1, 3))),
        "recommended_products": random.sample(product_ids, k=min(len(product_ids), 3))
    })

# Insert customers into the collection
customers_collection.insert_many(customers)

