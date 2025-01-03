from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['DatabaseName']
ratings_collection = db['Ratings']

# Rating constants and templates
POSSIBLE_RATINGS = [1, 2, 3, 4, 5]  # Only whole numbers 1-5

COMMENTS = {
    'positive': [
        "Excellent quality, very satisfied!",
        "Exceeded expectations, fantastic!",
        "Great value for money!",
        "Will definitely purchase again!",
        "Highly recommended to everyone!"
    ],
    'neutral': [
        "Quality is acceptable, average",
        "Meets expectations",
        "Average value for money",
        "Acceptable but not impressive",
        "It's okay, fairly standard"
    ],
    'negative': [
        "Quality could be better",
        "Not very satisfied",
        "Needs improvement",
        "Would not recommend",
        "Did not meet expectations"
    ]
}

def get_star_display(rating):
    """Convert numeric rating to star display"""
    return '★' * rating + '☆' * (5 - rating)

def generate_random_comment(rating):
    """Generate appropriate comment based on rating"""
    if rating >= 4:
        return random.choice(COMMENTS['positive'])
    elif rating == 3:
        return random.choice(COMMENTS['neutral'])
    else:
        return random.choice(COMMENTS['negative'])

def create_rating(rating_id, customer_id, product_id, num_ratings):
    """Create a single rating record"""
    rating = random.choice(POSSIBLE_RATINGS)
    random_days = random.randint(1, 365)
    rating_date = datetime.now() - timedelta(days=random_days)
    
    return {
        'rating_ID': rating_id,
        'customer_ID': customer_id,
        'product_ID': product_id,
        'rating': rating,
        'star_display': get_star_display(rating),
        'comment': generate_random_comment(rating),
        'rating_date': rating_date,
        'helpful_votes': random.randint(0, 50),
        'verified_purchase': random.choice([True, False, True, True]),
        'number_ratings': num_ratings
    }

def generate_random_ratings():
    """Generate random ratings"""
    try:
        customers = list(db.Customers.find({}, {'customer_ID': 1, '_id': 0}))
        products = list(db.Products.find({}, {'product_ID': 1, '_id': 0}))

        if not customers or not products:
            raise ValueError("No customer or product data found")

        ratings_collection.drop()
        rating_id = 1
        all_ratings = []

        for customer in customers:
            num_ratings = random.randint(3, 5)
            selected_products = random.sample(products, num_ratings)

            for product in selected_products:
                rating_doc = create_rating(
                    rating_id,
                    customer['customer_ID'],
                    product['product_ID'],
                    num_ratings
                )
                all_ratings.append(rating_doc)
                rating_id += 1

        if all_ratings:
            ratings_collection.insert_many(all_ratings)

        create_indexes()
        return f"Successfully generated {len(all_ratings)} ratings from {len(customers)} customers"

    except Exception as e:
        return f"Error generating ratings: {str(e)}"

def create_indexes():
    """Create necessary indexes"""
    ratings_collection.create_index([("rating_ID", 1)])
    ratings_collection.create_index([("customer_ID", 1)])
    ratings_collection.create_index([("product_ID", 1)])
    ratings_collection.create_index([("rating_date", -1)])


generate_random_ratings()

def test_star_display():
    """Test star display functionality - Optional for testing"""
    print("\n=== Star Display Test ===")
    test_ratings = [1.0, 2.0, 3.0, 4.0, 5.0]
    for rating in test_ratings:
        stars = get_star_display(rating)
        print(f"{rating} stars = {stars}")
