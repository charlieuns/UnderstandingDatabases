from pymongo import MongoClient
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
past_orders_collection = db['PastOrders']
inventory_collection = db['Inventory']
products_collection = db['Products']

# Prepare output
queries_and_results = []

# Query 1: Mobile_phone Sales performance by brand
sales_pipeline = [
    # 1. Extract each product in the products array.
    {
        "$unwind": "$products"
    },
    # 2. Match the product IDs in PastOrders with details.
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
    # 3. Only select the mobile phone product
        "$match": {
            "product_details.product_category": "mobile_phone"  # Filter by category
        }
    },
    # 4. Group data by mobile phone brand, calculate the total sales
    {
        "$group": {
            "_id": "$product_details.other_product_details.mobile_phone.brand",
            "total_sales": {
                "$sum": {"$multiply": ["$products.quantity", "$product_details.price"]}
            }
        }
    },
    {
    # 5. Sorting by total sales in descending order
        "$sort": {"total_sales": -1}
    }
]
# 6. Save query as Dataframe
sales_data = list(past_orders_collection.aggregate(sales_pipeline))
sales_df = pd.DataFrame(sales_data)
queries_and_results.append({
    "query": "Mobile_phone Sales performance by brand",
    "pipeline": sales_pipeline,
    "results": sales_data
})

# 7. Visualization: Use Seaborn to create bar chat
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
    # 1. ​Matching fresh product IDs in the Inventory collection
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
    # 2. Only select the mobile phone product
        "$match": {
            "product_details.product_category": "fresh_product"  # Filter by category
        }
    },
    # 3. Group data by category, compute the total inventory for each category.
    {
        "$group": {
            "_id": "$product_details.fresh_product_details.category",
            "total_inventory": {"$sum": "$inventory"}
        }
    },
    # 4. Sorting by total sales in descending order.
    {
        "$sort": {"total_inventory": -1}
    }
]
# 5. Save query as Dataframe
inventory_data = list(inventory_collection.aggregate(inventory_pipeline))
inventory_df = pd.DataFrame(inventory_data)
queries_and_results.append({
    "query": "Current Inventory performance",
    "pipeline": inventory_pipeline,
    "results": inventory_data
})

# 6. Visualization: Use Seaborn to create bar chat
sns.barplot(data=inventory_df, x='_id', y='total_inventory',palette="magma",hue='_id',legend=False)
for index, row in inventory_df.iterrows():
    plt.text(index, row['total_inventory'], f"{row['total_inventory']}", ha='center', va='bottom', fontsize=10)

plt.title('Current Fresh Product Inventory Levels', fontsize=14)
plt.xlabel('Fresh Product Category', fontsize=12)
plt.ylabel('Total Inventory', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Export Queries and Results to JSON
with open("TEST_query_4_(1-2)_and_results_.json", "w") as file:
    json.dump(queries_and_results, file, indent=4)

print("Queries and results exported")

