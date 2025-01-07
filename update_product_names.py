from pymongo import MongoClient
import random
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
products_collection = db["Products"]       

# Random name lists based on categories
bakery_random = ['Bun', 'Bread', 'Cake', 'Eclair', 'Croissant']
drinks_random = ['Cola', 'Professor Pupper', 'Water', 'Coffee', 'Tea']
fruit_veg_random = ['Tomato', 'Zuccini', 'Apple', 'Orange', 'Mango']

# Function to get a random name based on category
def get_random_name(category):
    if category == "bakery":
        return random.choice(bakery_random)
    elif category == "drinks":
        return random.choice(drinks_random)
    elif category == "fruit_veg":
        return random.choice(fruit_veg_random)
    return None

# Update each document in the products_collection
for document in products_collection.find():
    fresh_product_details = document.get("fresh_product_details", {})
    category = fresh_product_details.get("category")

    if category:
        random_name = get_random_name(category)
        if random_name:
            # Update the name field
            products_collection.update_one(
                {"_id": document["_id"]},
                {"$set": {"name": random_name}}
            )
            print(f"Updated document with _id {document['_id']} to name: {random_name}")
        else:
            print(f"No matching random names for category: {category}")
    else:
        print(f"Category not found for document with _id {document['_id']}")


book_name_inner = ['Introduction to', 'Advanced', 'Intermediate']
book_name_outer = ['Physics', 'Statistics', 'Mathematics', 'Philosophy', 'Geography']
author_name_inner = ['Beth', 'Roland', 'John', 'Arthur', 'David']
author_name_outer = ['A', 'B', 'C', 'R', 'P', 'T', 'Z', 'M', 'N']
publisher = ['Pengweng Books', 'Oxnard Press', 'Booksters']

