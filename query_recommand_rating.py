import pandas as pd
from pymongo import MongoClient

class RecommendationSystem:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_customer_summary(self, customer_id):
        """Aggregate past orders to summarize spending by category"""
        pipeline = [
            # Match the customer's orders
            {"$match": {"customer_ID": customer_id}},
            # Unwind products array
            {"$unwind": "$products"},
            # Lookup product details
            {
                "$lookup": {
                    "from": "Products",
                    "localField": "products.product_ID",
                    "foreignField": "product_ID",
                    "as": "product_details"
                }
            },
            # Unwind product details
            {"$unwind": "$product_details"},
            # Group by product category
            {
                "$group": {
                    "_id": "$product_details.product_category",
                    "total_spending": {
                        "$sum": {"$multiply": ["$products.quantity", "$product_details.price"]}
                    },
                    "total_purchases": {"$sum": "$products.quantity"},
                    "avg_spending": {
                        "$avg": {"$multiply": ["$products.quantity", "$product_details.price"]}
                    }
                }
            },
            # Sort by total spending
            {"$sort": {"total_spending": -1}},
            # Limit to top 2 categories
            {"$limit": 2}
        ]
        return list(self.db.PastOrders.aggregate(pipeline))

    def generate_recommendations(self, customer_id):
        """Generate product recommendations based on spending summary"""
        customer_summary = self.get_customer_summary(customer_id)

        if not customer_summary:
            print(f"No spending data for customer {customer_id}")
            return []

        recommendations = []
        for category_data in customer_summary:
            category = category_data["_id"]
            avg_spending = category_data["avg_spending"]

            # Fetch products in the category within the price range
            category_recommendations = list(self.db.Products.find(
                {
                    "product_category": category,
                    "price": {"$gte": avg_spending * 0.85, "$lte": avg_spending * 1.15}
                }
            ).sort("average_rating", -1).limit(5))

            recommendations.extend(category_recommendations)

        return recommendations

    def display_results(self, customer_id):
        """Display recommendations and spending summary"""
        customer_summary = self.get_customer_summary(customer_id)
        recommendations = self.generate_recommendations(customer_id)

        if customer_summary:
            print("\nCustomer Spending Summary:")
            summary_df = pd.DataFrame(customer_summary)
            summary_df.rename(columns={
                "_id": "Category",
                "total_spending": "Total Spending",
                "total_purchases": "Total Purchases",
                "avg_spending": "Avg Spending"
            }, inplace=True)
            print(summary_df.to_string(index=False))

        if recommendations:
            print("\nRecommended Products:")
            rec_df = pd.DataFrame(recommendations)
            rec_df = rec_df[["product_ID", "name", "product_category", "price", "average_rating"]]
            rec_df.rename(columns={
                "product_ID": "Product ID",
                "name": "Name",
                "product_category": "Category",
                "price": "Price",
                "average_rating": "Rating"
            }, inplace=True)
            print(rec_df.to_string(index=False))

# Main execution
if __name__ == "__main__":
    # MongoDB connection details
    MONGO_URI = "mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/"
    DB_NAME = "Amazone"

    # Initialize the recommendation system
    rec_system = RecommendationSystem(MONGO_URI, DB_NAME)

    # Display recommendations and spending summary for a specific customer
    CUSTOMER_ID = 1
    rec_system.display_results(CUSTOMER_ID)
