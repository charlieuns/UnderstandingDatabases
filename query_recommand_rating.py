import pandas as pd
from pymongo import MongoClient

class RecommendationSystem:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

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
        """Generate product recommendations based on spending summary"""
        customer_summary = self.get_customer_summary(customer_id)

        if not customer_summary:
            print(f"No spending data for customer {customer_id}")
            return []

        recommendations = []
        for category_data in customer_summary:
            category = category_data["_id"]

            # Fetch products in the category (no price range restriction)
            category_recommendations = list(self.db.Products.find(
                {"product_category": category}
            ).sort("average_rating", -1).limit(5))

            print(f"Customer {customer_id}, Category: {category}, Recommendations: {category_recommendations}")
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
                "total_purchases": "Total Purchases"
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
    MONGO_URI = "mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/"
    DB_NAME = "Amazone"

    rec_system = RecommendationSystem(MONGO_URI, DB_NAME)

    CUSTOMER_ID = 1
    rec_system.display_results(CUSTOMER_ID)
