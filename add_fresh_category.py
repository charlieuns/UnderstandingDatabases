from pymongo import MongoClient
import random
from datetime import datetime, timedelta

# Connect to MongoDB
# Connect to MongoDB
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
collection = db["Products"]  

# Define the possible category values
categories = ["drinks", "bakery", "fruit_veg"]

# Fetch documents with product_category as "fresh_product"
documents = collection.find({"product_category": "fresh_product"})

# Update each document with a random category
for doc in documents:
    random_category = random.choice(categories)
    result = collection.update_one(
        {"_id": doc["_id"]},  # Match the document by its unique _id
        {
            "$set": {
                "fresh_product_details.category": random_category
            }
        }
    )
    print(f"Document with _id {doc['_id']} updated with category: {random_category}")

# Summary
print("Random category assignment completed.")
