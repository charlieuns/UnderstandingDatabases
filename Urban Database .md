1. Customer Collection
{
  "customer_id": String,
  "name": String,
  "gender": String,
  "age": Number,
  "address_id": {
    "house_number": String,
    "street": String,
    "city": String,
    "postcode": String
  },
  "orders": [{
    "order_id": ObjectId,
    "order_date": Date,
    "total_cost": Number
  }],
  "ratings": [{
    "product_id": ObjectId,
    "rating": Number,
    "comment": String
  }]
}
2. Address Collection
{
  "address_id": String,
  "customer_id": ObjectId, // 引用Customer Collection
  "house_number": String,
  "street": String,
  "city": String,
  "postcode": String,
  "location": {
    "type": "Point",
    "coordinates": [Number, Number] // [longitude, latitude]
  },
  "address_type": String // "billing", "shipping" 
}
3. Product Collection
{
  "product_id": String,
  "product_name": String,
  "product_description": String,
  "product_type": String,  // "fresh" or "other"
  "product_category": String, // "bakery", "drinks", "fruits and vegetables", "books", "CDs", "mobile phones", "home appliances"
  "product_dimensions": {
    "length": Number,
    "width": Number,
    "height": Number
  },
  "weight": Number,
  "avg_rating": Number,
  "standard_price": Number,
  "cost_to_amazone": Number,
  "specific_attributes": {
    // Book
    "author": String,
    "publisher": String,
    "publication_year": Number,
    "isbn": String,

    // CD
    "artist": String,
    "number_of_tracks": Number,
    "total_playing_time": Number,
    "publisher": String,

    // Mobile phone
    "brand": String,
    "model": String,
    "color": String,
    "features": [String],

    // The home appliance
    "voltage": Number,
    "style": String,
    "color": String
  },
  "fresh_product_details": {
    "expiry_date": Date,
    "country_of_origin": String,
    "store_id": [ObjectId]
  }
}
5. Order Collection
 {
  "order_id": String,
  "customer_id": ObjectId, // 引用Customer Collection
  "order_type": String, // "fresh" 或 "other"
  "order_category": String, // "current" or "past"
  "order_items": [
    {
      "product_id": ObjectId, // 引用Product Collection
      "quantity": Number
    }
  ],
  "total_cost": Number,
  "order_date": Date,
  "delivery_address_id": ObjectId, // 引用Address Collection
  "delivery_partner_id": ObjectId, // 引用Partner Collection 
  "estimated_delivery_time": Date,
  "actual_delivery_time": Date,
  "order_status": String // "pending", "processing", "shipped", "delivered", "cancelled" 等
}
6.Partner Collection
{
  "partner_id": String,
  "name": String,
  "status": String,  // "active", "idle", "offline"
  "current_location": {
    "type": "Point",
    "coordinates": [Number, Number]
  },
  "current_task": {
    "order_id": ObjectId,
    "pickup_time": Date,
    "estimated_delivery_time": Date
  },
  "statistics": {
    "total_deliveries": Number,
    "avg_rating": Number,
    "total_earnings": Number,
    "success_rate": Number
  }
}
7. Store Collection
{
  "_id": ObjectId,
  "store_id": String,
  "name": String,
  "address": {
    "street": String,
    "city": String,
    "postcode": String
  },
  "location": {
    "type": "Point",
    "coordinates": [Number, Number]
  },
  "available_products": [ObjectId]
}
8. Inventory Collection
{
  "product_id": ObjectId,
  "date": Date,
  "quantity": Number,
  "warehouse": {
    "location": String,
    "name": String
  },
  "last_updated": Date
}


