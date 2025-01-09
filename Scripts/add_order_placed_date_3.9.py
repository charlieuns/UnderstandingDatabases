from pymongo import MongoClient
import random
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
collection = db["Customers"]       

# Function to generate a random date within the last year
def random_date_within_last_year():
    now = datetime.now()
    one_year_ago = now - timedelta(days=365)
    random_days = random.randint(0, 365)  # Random number of days within the last year
    random_date = one_year_ago + timedelta(days=random_days, seconds=random.randint(0, 86400))
    return random_date

# Fetch all documents in the Customers collection
documents = collection.find({})

# Update each document
for doc in documents:
    if "current_orders" in doc:  # Check if current_orders exists
        updated_orders = []
        for order in doc["current_orders"]:
            # Generate a random order_placed date
            random_date = random_date_within_last_year()
            order["order_placed"] = random_date
            updated_orders.append(order)
        
        # Update the document with new current_orders
        result = collection.update_one(
            {"_id": doc["_id"]},  # Match by _id
            {"$set": {"current_orders": updated_orders}}
        )
        print(f"Document with _id {doc['_id']} updated.")

