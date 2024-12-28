# Revised schema model for Understanding Databases Assignment 2

Customers = [{
'customer_ID':int (index),
'name': str,
'gender':str,
'age':int,
'addresses':[
    {
    'address_type':str,
    'house_number':int,
    'street':str,
    'city':str,
    'postcode':str
    }
],
'location':{
    'latitude': int,
    'longitude':int    
},
'cart':{
    'cart_total': float,
    'products': [ref <Products.product_ID>]
},
'current_orders':[{
     'order_ID':int,
     'order_total':float,
     'order_status'
     'partner_assigned':int,
     'order_placed':datetime,
     'order_destination':str,
     'products':
        {
        'product_ID':ref <Products.product_ID>,
        'quantity':int 
        }
    }],
'commonly_ordered_categories':[ref <Products.product_type],
'recommended_products':[ref <Products.product_ID>]
}]

PastOrders = [{
'order_ID':int,
'customer_ID':ref <Customers.customer_ID>,
'order_total':float,
'partner_assigned':ref <Partners.partner_ID,
'order_placed':datetime,
'order_delivered':datetime,
'products':
    {
    'product_ID':ref <Products.product_ID>,
    'quantity':int 
    }
}]

Products= [{
'product_ID': int,
'name': str,
'description': str,
'price': float,
'product_segment': str,
'product_category': str,
'fresh_product_details': {
	'dimensions': str,
	'weight': float,
	'expiry_date': date,
	'origin_country': str,
	'avg_rating': float,
	'morrizon_cost': float
	},
'other_product_details':{
	'dimensions': str,
	'shipping_weight': float,
	'avg_rating': float,
	'supplier_cost': float,
	'book':{
	  'author_name': str,
	  'publisher': str,
	  'year_of_publication': int,
	  'ISBN': str
	},
	'cd':{
	  'artist_name': str,
	  'number_tracks': int,
	  'total_playing_time': str,
	  'publisher': str
	},
	'mobile_phone':{
	  'brand': str,
	  'model': str,
	  'colour': str,
	  'features': str,
	},
	'home_appliance':{
	  'colour': str,
	  'voltage': int,
	  'style': str
    }
}
}]

Stores = [{
'address':{
    'house_number':int,
    'street':str,
    'city':str,
    'postcode':str
    }
},
'location':{
    'latitude': int,
    'longitude':int
},
'products_available':[{
    'product_ID':ref <Products.product_ID>,
    'quantity':int
}]
}]

Partners = [{
'partner_ID': int,
'name':str,
'gender':str,
'age':int,
'current_location': {
    'latitude': int,
    'longitude': int
},
'active':bool,
'on_errand':bool,
'current_task':ref <Orders.order_ID>,
'delivery_stats': {
	'total_deliveries': int
	'total_earnings': float  
	'rating': float
	}
}]

Inventory = [{
'product_ID': ref <Products.product_ID>,
'inventory': int,
'warehouse_name': str,
'location':{
    'latitude': int,
    'longitude': int
},
'date': date
}]

Ratings = [{
'product_ID': ref <Products.product_ID>,
'total_rating': int,
'number_ratings': int,
'ratings':[
    {
    'customer_ID':ref <Customers.customer_ID>,
    'rating': int
    }
]
}]

ToBeRecommended = [{
'category': ref <Products.product_category>,
'top_product_of_type': ref <Products.product_ID>
}]
