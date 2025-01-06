
import pymongo
from pymongo import MongoClient

conn_str = " "
client = MongoClient(conn_str, serverSelectionTimeoutMS=5000)

myDB = client["Amazone"]

top_categories = myDB.PastOrders.aggregate([
    {"$match": {"customer_ID": example}},
    {"$unwind": "$products"},
    {"$lookup": {
        "from": "Products",
        "localField": "products.product_ID",
        "foreignField": "product_ID",
        "as": "product_details"
    }},
    {"$group": {"_id":"$product_details.product_category",
                "count":{"$sum":1}}},
    {"$sort": {"count":-1}},
    {"$limit": 3},
    {"$project":{
        "count": 1,
        "category": "$_id", 
        "_id": 0}}
])

myDB.Customers.update_one({
    "q": {"customer_ID":example},
    "u": {"$set": {"commonly_ordered_categories":top_categories}},
    "upsert": True
})

recommended_products = myDB.Ratings.aggregate([
    {"$set": {"avg_rating": {"$divide": ["$total_rating", "$number_ratings"]}}},
    {"$lookup": {
        "from": "Products",
        "localField": "product_ID",
        "foreignField": "product_ID",
        "as": "product_details"
    }},
    {"$group": {
        "_id": {"$arrayElemAt": ["$product_details.product_category", 0]},
        "recommended_product": {"$max": "$avg_rating"},
        "product_ID": {"$first": "$product_ID"} 
    }},
    {"$project": {
        "top_product_of_type": "$product_ID",
        "category": "$_id", 
        "_id": 0 
    }}
])

myDB.ToBeRecommended.insert_many(recommended_products)

"""
for an example customer with ID = example, can be looped for all our customers
once the database is populated
"""

recommendations = myDB.Customers.aggregate([
    {"$match": {"customer ID": example}},
    {"$lookup": {
        "from": "ToBeRecommended",
        "localField": "commonly_ordered_categories",
        "foreignField": "category",
        "as": "recommendations"
    }},
    {"$project": {
        "product_ID": "$recommendations.product_ID"
    }}
])

myDB.Customers.update_one({
    "q": {"customer_ID":example},
    "u": {"$set": {"recommended_products":recommendations}},
    "upsert": True
})
