"""
First step is getting average ratings: total/number
Group by product category
Max rated in each category
Saved to ToBeRecommended
Use commonly ordered categories to select from that list
Save result to recommended products
"""
import pymongo
from pymongo import MongoClient

conn_str = "mongodb+srv://root:root@cluster0.gfqx6.mongodb.net/"
client = MongoClient(conn_str, serverSelectionTimeoutMS=5000)

myDB = client["Amazone"]

recommended_products = myDB.ratings.aggregate([
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