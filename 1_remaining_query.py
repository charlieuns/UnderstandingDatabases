from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd

# note: Find customers who haven’t made any purchases in the last 60 days, 
# along with additional operations such as sending promotional messages.

# Connect to MongoDB
conn_str = "mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/"
client = MongoClient(conn_str)
db = client["Amazone"]
customers_collection = db["Customers"]

# Step 1: Update all customers by adding an email field
customers = customers_collection.find({})  # Retrieve all customers
for customer in customers:
    customer_name = customer["name"]
    # Generate an email address using the customer's name
    email = f"{customer_name.lower().replace(' ', '_')}@example.com"
    # Update the document by adding the email field
    customers_collection.update_one(
        {"_id": customer["_id"]},  
        {"$set": {"email": email}}  
    )


# Step 1: Calculate the 60-day threshold date
duration = datetime.now() - timedelta(days=60)

# Step 2: Aggregation pipeline
pipeline = [
    {
        "$lookup": {  
            "from": "PastOrders",
            "localField": "customer_ID",
            "foreignField": "customer_ID",
            "as": "past_orders"
        }
    },
    {
        "$addFields": {  # Find the latest order date from both PastOrders and Customers
            "last_order_date": {
                "$max": [
                    {"$max": "$past_orders.order_placed"},  # Maximum date from PastOrders
                    {"$max": "$current_orders.order_placed"}  # Maximum date from current_orders in Customers
                ]
            }
        }
    },
    {
        "$match": {  # Filter customers with no orders in the last 60 days
            "last_order_date": {"$lt": duration}
        }
    },
    {
        "$project": {  
            "_id": 0,
            "customer_ID": 1,
            "name": 1,
            "email": 1,
            "last_order_date": 1
        }
    },
    {
        "$sort": { "last_order_date": 1 }  # Sort by last order date (oldest first)
    }
]
# Step 3: Execute the query
results = list(customers_collection.aggregate(pipeline))

# Step 4: Convert to DataFrame for easy viewing
df = pd.DataFrame(results)
print("Customers with no orders in the last 60 days:")
print(df)

# Step 5: Make a note for sending promotional emails
print("\nnote:")
for customer in results:
    print(f"Sending promotional email to {customer['name']} at {customer['email']}.")
