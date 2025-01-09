#Requirement 1：At least 2 queries indicating a customer ordering a fresh product. 
The query should include the assignment of pickup and delivery tasks to a partner based on location parameters. 
The query should return, e.g.,  details of the product ordered, delivery partner location and/ or ETA, and details of the delivery partner – name and ratings (if available).

from pymongo import MongoClient
import random
import string
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
customers_collection = db['Customers']
products_collection = db['Products']
stores_collection = db['Stores']
partners_collection = db['Partners']
inventory_collection = db['Inventory']

# Query 1: Assign the store, return details of products and stores
pipeline_query1 = [
# 1. Match customers and their orders based on order_ID
    {"$unwind": "$current_orders"},
    {"$match": {"current_orders.order_ID": 40}},  
    {"$unwind": "$current_orders.products"},

# 2. Find stores with ordered products in stock
    {"$lookup": { "from": "Stores","let": 
    {"productID": "$current_orders.products.product_ID",
     "orderQty": "$current_orders.products.quantity"},
    "pipeline": [{"$unwind": "$products_available"},
                 {"$match": 
                    {"$expr": 
                      {"$and": [{"$eq": ["$products_available.product_ID", "$$productID"]},
                          {"$gte": ["$products_available.quantity", "$$orderQty"]}]}
                    }}],
            "as": "store_details"}},

# 3. Associate product Information
    {"$unwind": "$store_details"},
    {"$lookup": {"from": "Products",
                 "localField": "current_orders.products.product_ID",
                 "foreignField": "product_ID",
                 "as": "product_details"}},
    {"$unwind": "$product_details"},

# 4. Find the closest store
    {"$addFields": {"store_distance": 
        {"$sqrt": {"$add": [{"$pow": [{"$subtract": ["$location.latitude", "$store_details.location.latitude"]}, 2]},
                        {"$pow": [{"$subtract": ["$location.longitude", "$store_details.location.longitude"]}, 2]}]
                   }
        }}},
    {"$sort": {"store_distance": 1}},
    {"$limit": 1},

# 5. Project final result
    {"$project": {"current_orders.order_ID": 1,
                  "current_orders.products.quantity": 1,
                  "product_details.name": 1,
                  "product_details.product_ID": 1,
                  "product_details.description": 1,
                  "product_details.product_segment": 1,
                  "product_details.product_category": 1,
                  "product_details.price": 1,
                  "store_details.address": 1,
                  "store_details.products_available.quantity": 1,
                  "store_details.store_ID": 1,  
                  "store_distance": 1}}
                  ]

result_query1 = list(db.Customers.aggregate(pipeline_query1))

from math import sqrt
import pprint
if result_query1:
    pprint.pprint(result_query1) 

# 6. Update the store inventory
if result_query1:
    for doc in result_query1:
        store_id = doc["store_details"]["store_ID"]
        product_id = doc["product_details"]["product_ID"]
        order_qty = doc["current_orders"]["products"]["quantity"] 
        
        db.Stores.update_one({"store_ID": store_id, "products_available.product_ID": product_id},
            {"$inc": {"products_available.$.quantity": -order_qty}} )
 
        updated_store = db.Stores.find_one(
            {"store_ID": store_id, "products_available.product_ID": product_id},
            {"products_available.$": 1} )
        
        updated_qty = updated_store["products_available"][0]["quantity"] if updated_store else "N/A"
        print(f"Updated stock for Store ID {store_id}, Product ID {product_id}. Updated Quantity: {updated_qty}.")

# Query 2: Assign the delivery partner, return partner details
pipeline_query2 = [
# 1. Match customers and their orders based on order_ID
    {"$unwind": "$current_orders"},
    {"$match": {"current_orders.order_ID": 40}}, 

# 2. Add location fields of the customer and the assigned store
    {"$addFields": {"customer_location": "$location"}},
    {"$addFields": {"assigned_store_ID": 5}},
    { "$lookup": { 
        "from": "Stores",
        "localField": "assigned_store_ID",
        "foreignField": "store_ID",
        "as": "store_details"
    }},
    {"$unwind": "$store_details"},
    {"$addFields": {"store_location": "$store_details.location"}},

# 3. Associate partners and find the nearest active partner not on errand
    {"$lookup": {
        "from": "Partners",
        "pipeline": [
            {"$match": {"active": True, "on_errand": False}},  
            {"$addFields": {"partner_distance": 
                {"$sqrt": {"$add": [{"$pow": [{"$subtract": ["$current_location.latitude", "$$store_location.latitude"]}, 2]},
                                    {"$pow": [{"$subtract": ["$current_location.longitude", "$$store_location.longitude"]}, 2]}]}}}},
            {"$sort": {"partner_distance": 1}}, 
            {"$limit": 1}  
        ],
        "let": {"store_location": "$store_location"},
        "as": "partner_details"
    }},
    {"$unwind": "$partner_details"},

# 4. Project the final result
    {"$project": {
        "current_orders.order_ID": 1,
        "assigned_store_ID": 1,
        "partner_details.partner_ID": 1,
        "partner_details.name": 1,
        "partner_details.gender": 1,
        "partner_details.age": 1,
        "partner_details.phone": 1,
        "partner_details.delivery_stats.rating": 1,
        "partner_distance": 1
    }}
]

result_query2 = list(db.Customers.aggregate(pipeline_query2))

if result_query2:
    pprint.pprint(result_query2) 

# 5. Update the delivery partner status
if result_query2:
    partner_id = result_query2[0]["partner_details"]["partner_ID"]
    order_id = result_query2[0]["current_orders"]["order_ID"]

    db.Partners.update_one(
        {"partner_ID": partner_id},  
        {"$set": {"on_errand": True,  
                "current_task": order_id }})

    print(f"Updated partner ID {partner_id} with current_task as {order_id} and on_errand set to True.")

# Query 3: Return delivery partner's location and ETA
from math import sqrt
pipeline_query3 = [

# 1. Match customers and their orders based on order_ID
    {"$unwind": "$current_orders"},  
    {"$match": {"current_orders.order_ID": 40}},

# 2. Add partner ID and lookup partner details
    {"$addFields": {"assigned_partner_ID": 4}},
    {"$lookup": {"from": "Partners",
                 "localField": "assigned_partner_ID",
                 "foreignField": "partner_ID",
                 "as": "partner_details"}},
    {"$unwind": "$partner_details"},

# 3. Project the partner location etc.
    {"$project": {"location": 1,
                  "current_orders.order_ID": 1,
                  "partner_details.partner_ID": 1,
                  "partner_details.name": 1,
                  "partner_details.current_location": 1,
                  "partner_details.delivery_stats.rating": 1}}]

result_query3 = list(db.Customers.aggregate(pipeline_query3))

# 4. Calculate ETA
if result_query3:
    for doc in result_query3:
        customer_loc = doc["location"]
        partner_loc = doc["partner_details"]["current_location"]
        distance = sqrt((customer_loc["latitude"] - partner_loc["latitude"]) ** 2 +
            (customer_loc["longitude"] - partner_loc["longitude"]) ** 2)
        average_speed = 30
        eta = round((distance / average_speed) * 60, 2)
        doc["ETA"] = eta
        pprint.pprint(doc) 
else:
    print("No partner could be assigned.")


# Query 4: when a customer cancelled the order of current fresh product after the assignment
# 1. Restore the store inventory
order_id = 40
store_id = 5
product_id = 2
order_qty = 2  

store_inventory = db.Stores.find_one(
    {"store_ID": store_id, "products_available.product_ID": product_id},
    {"products_available.$": 1} 
)

if store_inventory:
    available_quantity = store_inventory["products_available"][0]["quantity"]

    updated_inventory = available_quantity + order_qty
    
    db.Stores.update_one({"store_ID": store_id, "products_available.product_ID": product_id},
                         {"$inc": {"products_available.$.quantity": order_qty}})
    
    updated_store = db.Stores.find_one({"store_ID": store_id, "products_available.product_ID": product_id},
                                       {"products_available.$": 1})
    
    updated_qty = updated_store["products_available"][0]["quantity"] if updated_store else "N/A"
    
    print(f"Restored stock for Store ID {store_id}, Product ID {product_id}. Updated Quantity: {updated_qty}.")

# 2. restore the delivery partner status
partner_id = 4

db.Partners.update_one(
    {"partner_ID": partner_id},
    {"$set": {"on_errand": False,  
            "current_task": None }})

print(f"Updated partner ID {partner_id}:current_task set to None, on_errand set to False.")
