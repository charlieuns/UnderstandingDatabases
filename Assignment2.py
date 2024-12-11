# Schema model for Understanding Databases Assignment 2

Customers = [{
'CustomerID':int,
'Name': str,
'Gender':str,
'Age':int,
'Addresses':[
    {
    'AddressType':str,
    'HouseNumber':int,
    'Street':str,
    'City':str,
    'Postcode':str
    }
],
'CurrentOrders':[
    {
     'OrderID':int,
     'OrderTotal':int,
     'Partner':int,
     'Products':[
        {
        'ProductID':ref <FreshProducts.ProductID>,
        'Quantity':int 
        }
        ]
    }
]
}]

PastOrders = [{
'OrderID':int,
'CustomerID':ref <Customers.CustomerID>,
'OrderTotal':int,
'Products':[
    {
    'ProductID':ref <OtherProducts.ProductID>,
    'Quantity':int
    }
]
}]

FreshProducts = [{
'ProductID': int,
'Name': str,
'Description':str,
'Dimensions': str,
'Expiry': str,
'AvgRating':str,
'Price':str,
'Cost':str
}]


OtherProducts = [{
'ProductID': int,
'Name': str,
'Description':str,
'Dimensions': str,
'Weight':str,
'AvgRating':int,
'Price':int,
'Cost':int,
'BookDetails':{
    'AuthorName':str,
    'Publisher': str,
    'YearOfPublication':int,
    'ISBN': int
}
}]

Stores = [{
'Address':{
    'HouseNumber':int,
    'Street':str,
    'City':str,
    'Postcode':str
},
'Location':{
    'Latitude': int,
    'Longitude':int
},
'ProductsAvailable':[{
    'ProductID':ref <FreshProducts.ProductID>,
    'Quantity':int
}]
}]

Partners = [{
'PartnerID': int,
'Name':str,
'Gender':str,
'Age':int,
'CurrentLocation': {
    'Latitude': int,
    'Longitude': int
},
'Active':bool,
'OnErrand':bool,
'RecentOrders':[ref <Orders.OrderID>],
'PayOwed': int
}]

Inventory = [{
'ProductID': ref <OtherProducts.ProductID>,
'Inventory': int,
'WarehouseName': str,
'WarehouseLocation':{
    'Latitude': int,
    'Longitude': int
},
'Date': str
}]

Ratings = [{
'ProductID': ref <OtherProducts.ProductID>,
'TotalRating': int,
'NoRatings': int,
'Ratings':[
    {
    'CustomerID':ref <Customers.CustomerID>,
    'Rating': int
    }
]
}]

Recommendations = [{
'CustomerID': ref <Customers.CustomerID>,
'Products': [ref <OtherProducts.ProductID>]
}]


# Example values

Customers = {
'CustomerID':123456,
'Name':'Fred',
'Gender':'M',
'Age':56,
'Addresses':[
    {
    'AddressType':'Shipping',
    'HouseNumber':115,
    'Street':'Oxford Road',
    'City':'Manchester',
    'Postcode':'M13 1QA'
    }
],
'CurrentOrders':[
    {
     'OrderID':345678,
     'OrderTotal':12.1,
     'Partner':345678,
     'Products':[
        {
        'ProductID':101010,
        'Quantity':2 
        },
        {
        'ProductID':201010,
        'Quantity':1 
        }
        ]
    }
]
}

PastOrders = {
'OrderID':234567,
'CustomerID':123456,
'OrderTotal':24.5,
'Products':[
    {
    'ProductID':101010,
    'Quantity':2
    },
    {
    'ProductID':201010,
    'Quantity':1
    }
]
}

FreshProducts = {
'ProductID': 101010,
'Name': 'Courgette',
'Description':'Long, green vegetable',
'Dimensions': '20cm',
'Expiry':'12/12/2024',
'AvgRating':3.4,
'Price':0.8,
'Cost':0.4
}


OtherProducts = {
'ProductID': 202010,
'Name': 'The Trial',
'Description':'Novel about a distopian world',
'Dimensions': '15cm',
'Weight':'0.5kg',
'AvgRating':4.5,
'Price':0.8,
'Cost':0.4,
'BookDetails':{
    'AuthorName':'Franz Kafka',
    'Publisher': 'Penguin',
    'YearOfPublication': 1925,
    'ISBN': 9780241197790
}
}

Stores = {
'Address':{
    'HouseNumber':70,
    'Street':'Oxford Road',
    'City':'Manchester',
    'Postcode':'M14 5RB'
},
'Location':{
    'Latitude': 0,
    'Longitude':0
},
'ProductsAvailable':[{
    'ProductID':101010,
    'Quantity':10
}]
}

Partners = {
'PartnerID': 345678,
'Name':'Alex',
'Gender':'F',
'Age':28,
'CurrentLocation': {
    'Latitude': 0,
    'Longitude':0
},
'Active':True,
'OnErrand':True,
'RecentOrders':[345678, 234567],
'PayOwed': 150
}

Inventory = [{
'ProductID': 202010,
'Inventory': 12,
'WarehouseName':'Manchester',
'WarehouseLocation':{
    'Latitude': 0,
    'Longitude': 0
},
'Date':'12/12/2024'
}]

Ratings = {
'ProductID': 101010,
'TotalRating': 34,
'NoRatings': 10,
'Ratings':[
    {
    'CustomerID':123456,
    'Rating':4
    }
]
}

Recommendations = [{
'CustomerID': 123456,
'Products': [202010, 101010]
}]