from pymongo import MongoClient
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

client = MongoClient('mongodb+srv://example:example@cluster0.gfqx6.mongodb.net/')
db = client['Amazone']
partners_collection = db['Partners']

pipeline = [
# Firstly getting the fields we need
    {"$project":{"partner_ID":1,
                "earnings":"$delivery_stats.total_earnings",
                "_id":0}},
# Sorting the output in decreasing order of earnings
    {"$sort":{"earnings":-1}},
# Finding the top 5 partners for earnings
    {"$limit":5}
]

# Query: Partner earnings
partner_stats = list(partners_collection.aggregate(pipeline))

# Save query as Dataframe, ensuring partner_ID is treated as categorical
partner_df = pd.DataFrame(partner_stats)
partner_df['partner_ID'] = partner_df['partner_ID'].astype(dtype='str')
print(partner_df)

#Plot using Seaborn including text of earnings
plt.clf()
sns.barplot(data=partner_df, x='partner_ID', y='earnings', palette="viridis",legend=False)
for index, row in partner_df.iterrows():
    plt.text(index, row['earnings'] + 0.02, f"${row['earnings']:.2f}", ha='center', va='bottom', fontsize=10)
plt.title('Earnings by Partner', fontsize=14)
plt.xlabel('Partner ID', fontsize=12)
plt.ylabel('Total Earnings ($)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
