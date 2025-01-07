from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# MongoDB connection
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
ratings_collection = db['Ratings']
products_collection = db['Products']

def calculate_avg_rating(product_id):
    ratings_result = ratings_collection.find({'product_ID': product_id}, {'rating': 1, '_id': 0})
    ratings = [rating['rating'] for rating in ratings_result]
    return sum(ratings) / len(ratings)

# Computing ratings for fresh products
fresh_products = list(products_collection.find({'product_category':'fresh_product'}, {'product_ID':1, '_id':0}))

for product in fresh_products:
    product_ID = product['product_ID']
    avg_rating = calculate_avg_rating(product_ID)
    products_collection.update_one({'product_ID':product_ID}, {"$set":{"fresh_product_details.avg_rating": avg_rating}})

# Computing ratings for other products
other_categories=['book','cd','mobile_phone','home_appliance']
other_products = list(products_collection.find({'product_category':{"$in":other_categories}}, {'product_ID':1, '_id':0}))

for product in other_products:
    product_ID = product['product_ID']
    avg_rating = calculate_avg_rating(product_ID)
    products_collection.update_one({'product_ID':product_ID}, {"$set":{"other_product_details.avg_rating": avg_rating}})
