from pymongo import MongoClient
import random
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
collection = db["Products"]       

# Random name lists based on categories
bakery_random = ['Bun', 'Bread', 'Cake', 'Eclair', 'Croissant']
drinks_random = ['Cola', 'Professor Pupper', 'Water', 'Coffee', 'Tea']
fruit_veg_random = ['Tomato', 'Zuccini', 'Apple', 'Orange', 'Mango']

# Random name components for books
book_name_inner = ['Introduction to', 'Advanced', 'Intermediate']
book_name_outer = ['Physics', 'Statistics', 'Mathematics', 'Philosophy', 'Geography']
author_name_inner = ['Beth', 'Roland', 'John', 'Arthur', 'David']
author_name_outer = ['A', 'B', 'C', 'R', 'P', 'T', 'Z', 'M', 'N']
publisher_list = ['Pengweng Books', 'Oxnard Press', 'Booksters']

# Random name components for CDs
cd_name_inner = ['Sound of', 'Dancing with', 'Living with', 'Major', 'Minor']
cd_name_outer = ['Music', 'Apprehension', 'Joy', 'Sympathy', 'Silence']
artist_name_inner = ['Beth', 'Roland', 'John', 'Arthur', 'David']
artist_name_outer = ['A', 'B', 'C', 'R', 'P', 'T', 'Z', 'M', 'N']
cd_publisher = ['Big Band Studio', 'Small Band Studio', 'Medium Band Studio']

# Random name components for mobile phones
mobile_name_inner = ['1', '2', '3', '4', '5', '6']
mobile_name_outer = ['Pro', 'Pro Max', 'Plus']

# Random name list for home appliances
home_appliance_name = ['Washing Machine', 'Dryer', 'Air Fryer', 'Oven', 'Microwave', 'Dishwasher', 'Fridge']

# Function to get a random name based on category
def get_random_name(category):
    if category == "bakery":
        return random.choice(bakery_random)
    elif category == "drinks":
        return random.choice(drinks_random)
    elif category == "fruit_veg":
        return random.choice(fruit_veg_random)
    return None

# Function to generate random book details
def generate_random_book_details():
    book_name = f"{random.choice(book_name_inner)} {random.choice(book_name_outer)}"
    author_name = f"{random.choice(author_name_inner)} {random.choice(author_name_outer)}"
    publisher = random.choice(publisher_list)
    return book_name, author_name, publisher

# Function to generate random CD details
def generate_random_cd_details():
    cd_name = f"{random.choice(cd_name_inner)} {random.choice(cd_name_outer)}"
    artist_name = f"{random.choice(artist_name_inner)} {random.choice(artist_name_outer)}"
    publisher = random.choice(cd_publisher)
    return cd_name, artist_name, publisher

# Function to generate random mobile phone name
def generate_random_mobile_name():
    return f"{random.choice(mobile_name_inner)} {random.choice(mobile_name_outer)}"

# Function to generate random home appliance name
def generate_random_home_appliance_name():
    return random.choice(home_appliance_name)

# Update each document in the collection
for document in collection.find():
    product_category = document.get("product_category")
    
    if product_category in ["bakery", "drinks", "fruit_veg"]:
        fresh_product_details = document.get("fresh_product_details", {})
        category = fresh_product_details.get("category")

        if category:
            random_name = get_random_name(category)
            if random_name:
                # Update the name field
                collection.update_one(
                    {"_id": document["_id"]},
                    {"$set": {"name": random_name}}
                )
                print(f"Updated document with _id {document['_id']} to name: {random_name}")
            else:
                print(f"No matching random names for category: {category}")
        else:
            print(f"Category not found for document with _id {document['_id']}")
    
    elif product_category == "book":
        other_product_details = document.get("other_product_details", {})
        book_details = other_product_details.get("book", {})
        
        if book_details:
            book_name, author_name, publisher = generate_random_book_details()
            # Update the name, author_name, and publisher fields
            collection.update_one(
                {"_id": document["_id"]},
                {
                    "$set": {
                        "name": book_name,
                        "other_product_details.book.author_name": author_name,
                        "other_product_details.book.publisher": publisher
                    }
                }
            )
            print(f"Updated book document with _id {document['_id']} to name: {book_name}, author: {author_name}, publisher: {publisher}")
        else:
            print(f"Book details not found for document with _id {document['_id']}")
    
    elif product_category == "cd":
        other_product_details = document.get("other_product_details", {})
        cd_details = other_product_details.get("cd", {})
        
        if cd_details:
            cd_name, artist_name, publisher = generate_random_cd_details()
            # Update the name, artist_name, and publisher fields
            collection.update_one(
                {"_id": document["_id"]},
                {
                    "$set": {
                        "name": cd_name,
                        "other_product_details.cd.artist_name": artist_name,
                        "other_product_details.cd.publisher": publisher
                    }
                }
            )
            print(f"Updated CD document with _id {document['_id']} to name: {cd_name}, artist: {artist_name}, publisher: {publisher}")
        else:
            print(f"CD details not found for document with _id {document['_id']}")
    
    elif product_category == "mobile_phone":
        other_product_details = document.get("other_product_details", {})
        mobile_details = other_product_details.get("mobile_phone", {})
        
        if mobile_details:
            mobile_name = generate_random_mobile_name()
            # Update the name field
            collection.update_one(
                {"_id": document["_id"]},
                {"$set": {"name": mobile_name}}
            )
            print(f"Updated mobile_phone document with _id {document['_id']} to name: {mobile_name}")
        else:
            print(f"Mobile phone details not found for document with _id {document['_id']}")
    
    elif product_category == "home_appliance":
        other_product_details = document.get("other_product_details", {})
        home_appliance_details = other_product_details.get("home_appliance", {})
        
        if home_appliance_details:
            random_home_appliance_name = generate_random_home_appliance_name()
            # Update the name field
            collection.update_one(
                {"_id": document["_id"]},
                {"$set": {"name": random_home_appliance_name}}
            )
            print(f"Updated home_appliance document with _id {document['_id']} to name: {random_home_appliance_name}")
        else:
            print(f"Home appliance details not found for document with _id {document['_id']}")

