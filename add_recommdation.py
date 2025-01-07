import pandas as pd
from pymongo import MongoClient
import random

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

        for customer in customers:
            # Randomly select 5 products for the customer
            selected_products = random.sample(products, 5)
            product_ids = [product['product_ID'] for product in selected_products]

            # Update the Customers collection with the rated products
            self.db.Customers.update_one(
                {"customer_ID": customer["customer_ID"]},
                {"$set": {"rated_products": product_ids}}
            )

        print("Successfully assigned products to customers.")

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
        return list(self.db.PastOrders.aggregate(pipeline))

    def generate_recommendations(self, customer_id):
        """Generate product recommendations based on inventory levels"""
        customer_summary = self.get_customer_summary(customer_id)

        if not customer_summary:
            print(f"No spending data for customer {customer_id}")
            return []

        recommendations = []
        for category_data in customer_summary:
            category = category_data["_id"]

            # Fetch products in the category sorted by inventory in descending order
            category_product_ids = [
                product["product_ID"] for product in self.db.Products.find({"product_category": category}, {"product_ID": 1})
            ]
            category_recommendations = list(self.db.Inventory.find(
                {"product_ID": {"$in": category_product_ids}}
            ).sort("inventory", -1))  # Sort by inventory

            recommendations.extend(category_recommendations)

        # Select the top 5 products across both categories
        recommendations = sorted(recommendations, key=lambda x: x["inventory"], reverse=True)[:5]

        # Update recommended products in the Customers collection
        self.db.Customers.update_one(
            {"customer_ID": customer_id},
            {"$set": {"recommended_products": recommendations}}
        )

        return recommendations

    def display_results(self, customer_id):
        """Display recommendations, spending summary, and rated products"""
        # Fetch rated products
        customer = self.db.Customers.find_one({"customer_ID": customer_id}, {"rated_products": 1, "_id": 0})

        if customer and "rated_products" in customer:
            rated_products = customer["rated_products"]
            print("\nRated Products:")
            print(rated_products)
        else:
            print("\nNo rated products found for this customer.")

        # Spending summary
        customer_summary = self.get_customer_summary(customer_id)
        recommendations = self.generate_recommendations(customer_id)

        if customer_summary:
            print("\nCustomer Spending Summary:")
            summary_df = pd.DataFrame(customer_summary)
            summary_df.rename(columns={
                "_id": "Category",
                "total_spending": "Total Spending",
                "total_purchases": "Total Purchases"
            }, inplace=True)
            print(summary_df.to_string(index=False))

        if recommendations:
            print("\nRecommended Products:")
            rec_df = pd.DataFrame(recommendations)
            rec_df = rec_df[["product_ID", "inventory", "warehouse_name", "date"]]  # Display inventory-related fields
            rec_df.rename(columns={
                "product_ID": "Product ID",
                "inventory": "Inventory",
                "warehouse_name": "Warehouse",
                "date": "Date"
            }, inplace=True)
            print(rec_df.to_string(index=False))


# Main execution
if __name__ == "__main__":
    MONGO_URI = "mongodb://localhost:27017/"
    DB_NAME = "DatabaseName"

    rec_system = RecommendationSystem(MONGO_URI, DB_NAME)

    # Step 1: Assign 5 random products to each customer
    rec_system.assign_products_to_customers()

    # Step 2: Display results for a specific customer
    CUSTOMER_ID = 1
    rec_system.display_results(CUSTOMER_ID)
