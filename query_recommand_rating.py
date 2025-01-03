import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient

try:
    with MongoClient('mongodb://localhost:27017/') as client:
        db = client['DatabaseName']
        print("sucessful")
        
        # test
        customers = db['Customers'].find_one()
        print(f"example：{customers}")
except Exception as e:
    print(f"erro：{e}")

# Collections
customers_collection = db['Customers']
products_collection = db['Products']
past_orders_collection = db['PastOrders']
inventory_collection = db['Inventory']
ratings_collection = db['Ratings']

# Customer ID 
customer_id = 9

class RecommendationSystem:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def get_recommendations_pipeline(self, customer_id):
        """Core recommendation aggregation pipeline"""
        current_time = datetime.now()
        day_ago = current_time - timedelta(days=1)
        
        pipeline = [
            # 1. Get browsing and purchase history in parallel
            {
                "$facet": {
                    "browsing_history": [
                        {
                            "$match": {"customer_ID": customer_id}
                        },
                        {
                            "$sort": {"view_time": -1}
                        },
                        {
                            "$limit": 15
                        },
                        {
                            "$group": {
                                "_id": None,
                                "viewed_products": {"$push": "$product_ID"},
                                "category_views": {
                                    "$push": {
                                        "category": "$product_category",
                                        "view_time": "$view_time"
                                    }
                                }
                            }
                        }
                    ],
                    "purchase_history": [
                        {
                            "$match": {"customer_ID": customer_id}
                        },
                        {
                            "$unwind": "$products"
                        },
                        {
                            "$group": {
                                "_id": "$products.category",
                                "avg_price": {"$avg": "$products.price"},
                                "purchase_count": {"$sum": 1}
                            }
                        }
                    ]
                }
            }
        ]
        
        return pipeline
    
    def process_and_visualize(self, customer_id):
        """Process and visualize customer data"""
        pipeline = self.get_recommendations_pipeline(customer_id)
        results = list(self.db.BrowsingHistory.aggregate(pipeline))
        
        if not results:
            print("No data found for this customer")
            return
        
        browsing_data = results[0].get('browsing_history', [])
        purchase_data = results[0].get('purchase_history', [])
        
        fig = plt.figure(figsize=(15, 10))
        
        # 1. browsing_history_data
        if browsing_data:
            plt.subplot(2, 2, 1)
            category_views = pd.DataFrame(browsing_data[0]['category_views'])
            category_counts = category_views['category'].value_counts()
            
            sns.barplot(x=category_counts.values, y=category_counts.index)
            plt.title('Category View Distribution')
            plt.xlabel('Number of Views')
            
        # 2. purchase_history_data
        if purchase_data:
            plt.subplot(2, 2, 2)
            purchase_df = pd.DataFrame(purchase_data)
            sns.scatterplot(data=purchase_df, x='avg_price', y='purchase_count', 
                          size='purchase_count', hue='_id')
            plt.title('Purchase History Analysis')
            plt.xlabel('Average Price')
            plt.ylabel('Purchase Count')
            
        # 3. browsing_timeline
        if browsing_data:
            plt.subplot(2, 2, 3)
            category_views['view_time'] = pd.to_datetime(category_views['view_time'])
            sns.lineplot(data=category_views, x='view_time', y='category')
            plt.title('Browsing Timeline')
            plt.xticks(rotation=45)
            
        # 4. recommendations
        recommendations = self.get_final_recommendations(customer_id)
        if recommendations:
            plt.subplot(2, 2, 4)
            rec_df = pd.DataFrame(recommendations)
            sns.barplot(data=rec_df, x='product_name', y='score')
            plt.title('Top Recommendations')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    def get_final_recommendations(self, customer_id):
        """Get final product recommendations"""
        pipeline = self.get_recommendations_pipeline(customer_id)
        pipeline.extend([
            {
                "$lookup": {
                    "from": "Products",
                    "let": {
                        "viewed_products": {
                            "$first": "$browsing_history.viewed_products"
                        }
                    },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$not": [{"$in": ["$product_ID", "$$viewed_products"]}]
                                }
                            }
                        },
                        {"$sort": {"rating": -1}},
                        {"$limit": 5}
                    ],
                    "as": "recommendations"
                }
            }
        ])
        
        results = list(self.db.BrowsingHistory.aggregate(pipeline))
        return results[0].get('recommendations', []) if results else []
    def generate_report(self, customer_id):
        """Generate a detailed report for a customer"""
        # visualize customer data
        fig = self.process_and_visualize(customer_id)
        
        # Get final recommendations
        recommendations = self.get_final_recommendations(customer_id)
        if recommendations:
            rec_df = pd.DataFrame(recommendations)
            rec_df = rec_df[['name', 'category', 'price', 'score']].rename(columns={
                'name': 'Product Name',
                'category': 'Category',
                'price': 'Price ($)',
                'score': 'Score'
            })
            
            print("\nRecommended Products Table:")
            print("=" * 80)
            print(rec_df.to_string(index=False))
        
        # browse history
        browsing_data = list(self.db.BrowsingHistory.find(
            {"customer_ID": customer_id}
        ).limit(10))
        
        if browsing_data:
            browsing_df = pd.DataFrame(browsing_data)
            browsing_df['view_time'] = pd.to_datetime(browsing_df['view_time'])
            browsing_df = browsing_df[['product_category', 'view_time']].rename(columns={
                'product_category': 'Category',
                'view_time': 'View Time'
            })
            
            print("\nRecent Browsing History Table:")
            print("=" * 80)
            print(browsing_df.to_string(index=False))
    def analyze_system_performance(self, customer_id):
        """Analyze system performance for a customer"""
        pipeline = [
            {"$match": {"customer_ID": customer_id}},
            {
                "$group": {
                    "_id": None,
                    "total_views": {"$sum": 1},
                    "unique_categories": {"$addToSet": "$product_category"},
                    "avg_view_time": {"$avg": {"$subtract": ["$end_time", "$view_time"]}}
                }
            }
        ]
        
        results = list(self.db.BrowsingHistory.aggregate(pipeline))
        
        if results:
            performance_data = results[0]
            
            # Creating performance analysis charts
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # category views and total views
            metrics = ['Total Views', 'Unique Categories']
            values = [performance_data['total_views'], 
                     len(performance_data['unique_categories'])]
            
            ax1.bar(metrics, values)
            ax1.set_title('Browsing Metrics')
            
            # avg view time
            ax2.pie([performance_data['avg_view_time']], 
                   labels=['Avg View Time (s)'],
                   autopct='%1.1f%%')
            ax2.set_title('Average View Time Distribution')
            
            plt.tight_layout()
            plt.show()
