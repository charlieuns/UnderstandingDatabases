from pymongo import MongoClient
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
past_orders_collection = db['PastOrders']
inventory_collection = db['Inventory']
products_collection = db['Products']

# Query 1: Mobile_phone Sales performance by brand
sales_pipeline = [
    {
        "$unwind": "$products"
    },
    {
        "$lookup": {
            "from": "Products",
            "localField": "products.product_ID",
            "foreignField": "product_ID",
            "as": "product_details"
        }
    },
    {
        "$unwind": "$product_details"
    },
    {
        "$match": {
            "product_details.product_category": "mobile_phone"  # Filter by category
        }
    },
    {
        "$group": {
            "_id": "$product_details.other_product_details.mobile_phone.brand",
            "total_sales": {
                "$sum": {"$multiply": ["$products.quantity", "$product_details.price"]}
            }
        }
    },
    {
        "$sort": {"total_sales": -1}
    }
]

sales_data = list(past_orders_collection.aggregate(sales_pipeline))
sales_df = pd.DataFrame(sales_data)

sns.barplot(data=sales_df, x='_id', y='total_sales', palette="viridis",hue='_id',legend=False)
for index, row in sales_df.iterrows():
    plt.text(index, row['total_sales'], f"${row['total_sales']:.2f}", ha='center', va='bottom', fontsize=10)
    
plt.title('Sales performance by brand', fontsize=14)
plt.xlabel('Phones Brand', fontsize=12)
plt.ylabel('Total Sales ($)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Query 2: Current Inventory performance
inventory_pipeline = [
    {
        "$lookup": {
            "from": "Products",
            "localField": "product_ID",
            "foreignField": "product_ID",
            "as": "product_details"
        }
    },
    {
        "$unwind": "$product_details"
    },
    {
        "$group": {
            "_id": "$product_details.product_category",
            "total_inventory": {"$sum": "$inventory"}
        }
    },
    {
        "$sort": {"total_inventory": -1}
    }
]

inventory_data = list(inventory_collection.aggregate(inventory_pipeline))
inventory_df = pd.DataFrame(inventory_data)

sns.barplot(data=inventory_df, x='_id', y='total_inventory',palette="magma",hue='_id',legend=False)
for index, row in inventory_df.iterrows():
    plt.text(index, row['total_inventory'], f"{row['total_inventory']}", ha='center', va='bottom', fontsize=10)

plt.title('Current Inventory Levels by Product Category', fontsize=14)
plt.xlabel('Product Category', fontsize=12)
plt.ylabel('Total Inventory', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
