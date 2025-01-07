import pandas as pd
from pymongo import MongoClient
import random
from tabulate import tabulate  # sudo pip install tabulate
class RecommendationSystem:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def assign_products_to_customers(self):
        """Assign 5 products to each customer and update Customers collection"""
        customers = list(self.db.Customers.find({}, {"customer_ID": 1, "_id": 0}))
        products = list(self.db.Products.find({}, {"product_ID": 1, "_id": 0}))

        if not customers or not products:
            print("No customer or product data found.")
            return

        table_data = []  # store the results for display

        for customer in customers:
            # Randomly select 5 products for the customer
            selected_products = random.sample(products, 5)
            product_ids = [product['product_ID'] for product in selected_products]

            # Update the Customers collection with the rated products
            self.db.Customers.update_one(
                {"customer_ID": customer["customer_ID"]},
                {"$set": {"rated_products": product_ids}}
            )

            # store the results for display
            table_data.append({"Customer ID": customer["customer_ID"], "Rated Products": product_ids})

        # show the results
        print("\n=== Assigned Products to Customers ===")
        print(tabulate(pd.DataFrame(table_data), headers="keys", tablefmt="grid"))

    def get_customer_summary(self, customer_id):
        """Aggregate past orders to summarize spending by category"""
        pipeline = [
            {"$match": {"customer_ID": customer_id}},
            {"$unwind": "$products"},
            {
                "$lookup": {
                    "from": "Products",
                    "localField": "products.product_ID",
                    "foreignField": "product_ID",
                    "as": "product_details"
                }
            },
            {"$unwind": "$product_details"},
            {
                "$group": {
                    "_id": "$product_details.product_category",
                    "total_spending": {
                        "$sum": {"$multiply": ["$products.quantity", "$product_details.price"]}
                    },
                    "total_purchases": {"$sum": "$products.quantity"},
                }
            },
            {"$sort": {"total_spending": -1}},
            {"$limit": 2}
        ]
        customer_summary = list(self.db.PastOrders.aggregate(pipeline))

        # show the results
        print("\n=== Customer Spending Summary ===")
        print(tabulate(pd.DataFrame(customer_summary), headers="keys", tablefmt="grid"))

        return customer_summary

    def generate_recommendations(self, customer_id):
        """Generate product recommendations based on spending summary"""
        customer_summary = self.get_customer_summary(customer_id)

        if not customer_summary:
            print(f"No spending data for customer {customer_id}")
            return []

        recommendations = []
        for category_data in customer_summary:
            category = category_data["_id"]

            # Fetch products in the category sorted by average_rating
            category_recommendations = list(self.db.Products.find(
                {"product_category": category},
                {"product_ID": 1, "price": 1, "product_category": 1, "average_rating": 1}
            ).sort("average_rating", -1))

            recommendations.extend(category_recommendations)

        # Limit to top 5 products across the 2 categories
        recommendations = sorted(recommendations, key=lambda x: x["average_rating"], reverse=True)[:5]

        # Update recommended products in the Customers collection
        self.db.Customers.update_one(
            {"customer_ID": customer_id},
            {"$set": {"recommended_products": recommendations}}
        )

        # show the results
        print("\n=== Recommended Products ===")
        recommendations_df = pd.DataFrame(recommendations)
        recommendations_df = recommendations_df[["product_ID", "price", "product_category", "average_rating"]]
        recommendations_df.rename(columns={
            "product_ID": "Product ID",
            "price": "Price",
            "product_category": "Category",
            "average_rating": "Rating"
        }, inplace=True)
        print(tabulate(recommendations_df, headers="keys", tablefmt="grid"))

        return recommendations

    def display_results(self, customer_id):
        """Display recommendations, spending summary, and rated products"""
        # Fetch rated products
        customer = self.db.Customers.find_one({"customer_ID": customer_id}, {"rated_products": 1, "_id": 0})

        if customer and "rated_products" in customer:
            rated_products = customer["rated_products"]
            rated_products_df = pd.DataFrame({"Rated Products": rated_products})
            print("\n=== Rated Products ===")
            print(tabulate(rated_products_df, headers="keys", tablefmt="grid"))
        else:
            print("\nNo rated products found for this customer.")

        # Spending summary and recommendations
        self.get_customer_summary(customer_id)
        self.generate_recommendations(customer_id)


# Main execution
if __name__ == "__main__":
    MONGO_URI = "mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/"
    DB_NAME = "Amazone"

    rec_system = RecommendationSystem(MONGO_URI, DB_NAME)

    # Step 1: Assign 5 random products to each customer
    rec_system.assign_products_to_customers()

    # Step 2: Display results for a specific customer
    CUSTOMER_ID = 1
    rec_system.display_results(CUSTOMER_ID)
