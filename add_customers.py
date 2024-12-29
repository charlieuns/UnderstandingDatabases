from pymongo import MongoClient
import random
import string

# Connect to MongoDB
client = MongoClient('mongodb://')
db = client['YourDatabaseName']
customers_collection = db['Customers']

# Function to generate UK postcodes
def generate_uk_postcode():
    area = random.choice(string.ascii_uppercase)  # One letter for the area
    district = str(random.randint(1, 99))  # One or two digits for the district
    outward_code = f"{area}{district}"

    sector = str(random.randint(0, 9))  # Single digit
    unit = ''.join(random.choices(string.ascii_uppercase, k=2))  # Two random letters
    inward_code = f"{sector}{unit}"

    return f"{outward_code} {inward_code}"

# list to generate customer random names
male_names = ["Adam", "Charlie", "Edward", "George", "Jack", "Liam", "Nathan", "Oscar", "Paul", "Sam"]
female_names = ["Beth", "Diana", "Fiona", "Hannah", "Ivy", "Karen", "Mona", "Olivia", "Rachel", "Tina"]
last_initials = [chr(i) for i in range(65, 91)]  # A-Z

# list to generate addresses
uk_cities = ["London", "Manchester", "Birmingham", "Leeds", "Glasgow", "Liverpool", "Bristol", "Sheffield", "Edinburgh", "Cardiff"]
uk_streets = ["High Street", "Station Road", "Church Lane", "Victoria Road", "Park Avenue", "Main Street", "Mill Lane", "The Crescent", "Queensway", "King Street"]
address_types = ["Home", "Work"]

# Generate random product IDs
product_ids = [i for i in range(101, 201)]

# initialising empty arrays
customers = []
order_id = 1

# Create 10 male and 10 female customers
for i in range(20):
    if i < 10:
        first_name = male_names[i]
        gender = "Male"
    else:
        first_name = female_names[i - 10]
        gender = "Female"
    
    last_initial = random.choice(last_initials)
    name = f"{first_name} {last_initial}"
    age = random.randint(18, 70)
    
    # Generate 2-3 addresses for each customer
    addresses = [
        {
            "AddressType": random.choice(address_types),
            "HouseNumber": random.randint(1, 999),
            "Street": random.choice(uk_streets),
            "City": random.choice(uk_cities),
            "Postcode": generate_uk_postcode()  # Use UK postcode generator function
        }
        for _ in range(random.randint(1, 3))
    ]
    
    # Generate 2-3 current orders for each customer
    current_orders = []
    for _ in range(2):
        products = [
            {
                "ProductID": random.choice(product_ids),
                "Quantity": random.randint(1, 10)
            }
            for _ in range(random.randint(1, 5))  # Each order has 1-5 products
        ]
        current_orders.append({
            "OrderID": order_id,
            "OrderTotal": sum(p['Quantity'] * random.randint(10, 100) for p in products),
            "Partner": random.randint(1, 10),  # Random partner ID
            "Products": products
        })
        order_id += 1
    
    # Create the customer document
    customers.append({
        "CustomerID": i + 1,
        "Name": name,
        "Gender": gender,
        "Age": age,
        "Addresses": addresses,
        "CurrentOrders": current_orders
    })

# Insert customers into the collection
customers_collection.insert_many(customers)
