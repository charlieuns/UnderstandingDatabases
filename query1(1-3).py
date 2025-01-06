#Requirement 1：At least 2 queries indicating a customer ordering a fresh product. 
The query should include the assignment of pickup and delivery tasks to a partner based on location parameters. 
The query should return, e.g.,  details of the product ordered, delivery partner location and/ or ETA, and details of the delivery partner – name and ratings (if available).

# Query 1: Assign the store, return details of products and stores, and update assignedStore in the Customers collection
pipeline_query1 = [
# 1.Match customers and their orders
    {"$match": {"customer_ID": 20}},
    {"$unwind": "$current_orders"},
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
                  "product_details.name": 1,
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

print("Query 1 Result:")
for doc in result_query1:
    print(doc)

# Query 2: Assign the delivery partner, return partner details and update assignedPartner in the Customers collection
pipeline_query2 = [
# 1. Match customers and their orders
    {"$match": {"customer_ID": 20}},
    {"$unwind": "$current_orders"},
    {"$match": {"current_orders.order_ID": 40}},

#2. Add location fields of the customer and the assigned store
    {"$addFields": {"customer_location": "$location"}},
    {"$addFields": {"assigned_store_ID": 5}},
    { "$lookup": { "from": "Stores",
                   "localField": "assigned_store_ID",
                   "foreignField": "store_ID",
                   "as": "store_details"}},
    {"$unwind": "$store_details"},
    {"$addFields": {"store_location": "$store_details.location"}},

#3. Associate partners and find the nearest partner
    {"$lookup": {"from": "Partners",
            "pipeline": [{"$addFields": {"partner_distance": 
                {"$sqrt": {"$add": [{"$pow": [{"$subtract": ["$current_location.latitude", "$$store_location.latitude"]}, 2]},
                                    {"$pow": [{"$subtract": ["$current_location.longitude", "$$store_location.longitude"]}, 2]}]}}}},
                {"$sort": {"partner_distance": 1}},
                {"$limit": 1}],
            "let": {"store_location": "$store_location"},
            "as": "partner_details"}},
    {"$unwind": "$partner_details"},

#4. Project the final result
    {"$project": {"current_orders.order_ID": 1,
                  "assigned_store_ID": 1,
                  "partner_details.partner_ID": 1,
                  "partner_details.name": 1,
                  "partner_details.gender": 1,
                  "partner_details.age": 1,
                  "partner_details.phone": 1,
                  "partner_details.delivery_stats.rating": 1,
                  "partner_distance": 1}}]

result_query2 = list(db.Customers.aggregate(pipeline_query2))

print("Query 2 Result:")
for doc in result_query2:
    print(doc)

# Query 3: Return delivery partner's location and ETA
from math import sqrt
pipeline_query3 = [

# 1. Match customers and their orders
    {"$match": {"customer_ID": 20}},
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
        print("Query 3 Result:", doc)
else:
    print("No partner could be assigned.")
