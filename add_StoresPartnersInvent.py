from pymongo import MongoClient
import random
import string
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://')
db = client['DatabaseName']
stores_collection = db['Stores']
partners_collection = db['Partners']
inventory_collection = db['Inventory']

# Helper function to generate random location within the UK
def generate_uk_location():
    latitude = random.uniform(49.3, 58.6)  # UK latitude bounds
    longitude = random.uniform(-8.1, 1.8)  # UK longitude bounds
    return latitude, longitude

# Fetch product IDs from Products collection
product_ids = [product["product_ID"] for product in db.Products.find({}, {"product_ID": 1})]

# Part 3: Populate Stores Collection
stores = []
for i in range(1, 6):
    latitude, longitude = generate_uk_location()
    stores.append({
        "store_ID": i,
        "address": {
            "house_number": random.randint(1, 999),
            "street": random.choice(["High Street", "Station Road", "Church Lane", "Victoria Road", "Park Avenue"]),
            "city": random.choice(["London", "Manchester", "Birmingham", "Leeds", "Glasgow"]),
            "postcode": f"{random.choice(string.ascii_uppercase)}{random.randint(1, 99)} {random.randint(0, 9)}{''.join(random.choices(string.ascii_uppercase, k=2))}"
        },
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "products_available": [
            {"product_ID": random.choice(product_ids), "quantity": random.randint(10, 100)} for _ in range(5)
        ]
    })

stores_collection.insert_many(stores)

# Part 4: Populate Partners Collection
partners = []
for i in range(1, 6):
    latitude, longitude = generate_uk_location()
    partners.append({
        "partner_ID": i,
        "name": random.choice(["Alice", "Bob", "Chase", "Diana", "Ethan"]),
        "gender": random.choice(["Male", "Female"]),
        "age": random.randint(18, 60),
        "current_location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "active": random.choice([True, False]),
        "on_errand": random.choice([True, False]),
        "current_task": random.randint(1001, 1010) if random.choice([True, False]) else None,
        "delivery_stats": {
            "total_deliveries": random.randint(50, 200),
            "total_earnings": round(random.uniform(10000, 50000), 2),
            "rating": round(random.uniform(3.5, 5.0), 1)
        }
    })

partners_collection.insert_many(partners)

# Part 5: Populate Inventory Collection
inventory = []
for product_id in product_ids: 
    latitude, longitude = generate_uk_location()
    inventory.append({
        "product_ID": product_id,
        "inventory": random.randint(50, 500),
        "warehouse_name": f"Warehouse_{random.randint(1, 5)}",
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "date": datetime.now().strftime("%Y-%m-%d")
    })

inventory_collection.insert_many(inventory)

print("Data for Stores, Partners, and Inventory collections has been inserted successfully!")