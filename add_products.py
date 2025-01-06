from pymongo import MongoClient
import random
import string
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
products_collection = db['Products']

categories = ["bakery", "drinks", "fruits_and_veg"]

# Helper function to generate random strings
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Generate fresh product details
def generate_fresh_product_details():
    return {
        "category": random.choice(categories),
        "dimensions": f"{random.randint(5, 20)}x{random.randint(5, 20)}x{random.randint(5, 20)} cm",
        "weight": round(random.uniform(0.1, 5), 2),  # Random weight between 0.1kg and 5kg
        "expiry_date": datetime.now() + timedelta(days=random.randint(1, 30)),  # Random expiry in the next 30 days
        "origin_country": random.choice(["UK", "Spain", "Italy", "France", "USA"]),
        "avg_rating": round(random.uniform(1, 5), 1),  # Random rating between 1 and 5
        "morrizon_cost": round(random.uniform(2, 20), 2)  # Random cost between 2 and 20
    }

# Generate other product details (for book, cd, mobile phone, home appliance)
def generate_other_product_details(product_type):
    if product_type == 'book':
        return {
            "dimensions": f"{random.randint(10, 30)}x{random.randint(10, 30)}x{random.randint(2, 5)} cm",
            "shipping_weight": round(random.uniform(0.5, 2), 2),  # Random shipping weight between 0.5kg and 2kg
            "avg_rating": round(random.uniform(1, 5), 1),  # Random rating between 1 and 5
            "supplier_cost": round(random.uniform(5, 30), 2),  # Random supplier cost between 5 and 30
            "book": {
                "author_name": generate_random_string(),
                "publisher": generate_random_string(),
                "year_of_publication": random.randint(2000, 2023),
                "ISBN": generate_random_string(13)
            }
        }
    elif product_type == 'cd':
        return {
            "dimensions": f"{random.randint(10, 20)}x{random.randint(10, 20)}x{random.randint(1, 2)} cm",
            "shipping_weight": round(random.uniform(0.2, 0.5), 2),  # Random shipping weight between 0.2kg and 0.5kg
            "avg_rating": round(random.uniform(1, 5), 1),  # Random rating between 1 and 5
            "supplier_cost": round(random.uniform(5, 20), 2),  # Random supplier cost between 5 and 20
            "cd": {
                "artist_name": generate_random_string(),
                "number_tracks": random.randint(8, 20),
                "total_playing_time": f"{random.randint(30, 60)}:{random.randint(0, 59)}",
                "publisher": generate_random_string()
            }
        }
    elif product_type == 'mobile_phone':
        return {
            "dimensions": f"{random.randint(5, 20)}x{random.randint(5, 20)}x{random.randint(1, 2)} cm",
            "shipping_weight": round(random.uniform(0.2, 0.7), 2),  # Random shipping weight between 0.2kg and 0.7kg
            "avg_rating": round(random.uniform(1, 5), 1),  # Random rating between 1 and 5
            "supplier_cost": round(random.uniform(50, 300), 2),  # Random supplier cost between 50 and 300
            "mobile_phone": {
                "brand": random.choice(["Samsung", "Apple", "Huawei", "Google", "Nokia"]),
                "model": generate_random_string(),
                "colour": random.choice(["Black", "White", "Silver", "Gold", "Blue"]),
                "features": generate_random_string(20)
            }
        }
    elif product_type == 'home_appliance':
        return {
            "dimensions": f"{random.randint(20, 60)}x{random.randint(20, 60)}x{random.randint(10, 30)} cm",
            "shipping_weight": round(random.uniform(1, 10), 2),  # Random shipping weight between 1kg and 10kg
            "avg_rating": round(random.uniform(1, 5), 1),  # Random rating between 1 and 5
            "supplier_cost": round(random.uniform(20, 100), 2),  # Random supplier cost between 20 and 100
            "home_appliance": {
                "colour": random.choice(["Black", "White", "Silver"]),
                "voltage": random.choice([110, 230]),
                "style": random.choice(["Modern", "Classic", "Retro"])
            }
        }

# Generate 10 products for each category
categories = ['fresh_product', 'book', 'cd', 'mobile_phone', 'home_appliance']
products = []

product_id = 1
for category in categories:
    for _ in range(10):  # Generate 10 products per category
        if category == 'fresh_product':
            product_details = generate_fresh_product_details()
        else:
            product_details = generate_other_product_details(category)
        
        product = {
            "product_ID": product_id,
            "name": f"{category.capitalize()} {product_id}",
            "description": f"A {category} product description.",
            "price": round(random.uniform(5, 500), 2),
            "product_segment": random.choice(["Consumer", "Luxury", "Essential"]),
            "product_category": category,
            "fresh_product_details" if category == 'fresh_product' else "other_product_details": product_details
        }
        
        products.append(product)
        product_id += 1

# Insert products into the collection
products_collection.insert_many(products)
