// The current database to use.
use("Amazone");

// Step 1: Retrieve user information and location
const user = db.Customers.findOne({ customer_ID: 1 }); // Assuming the user ID is 1

// Step 2: Create a 2dsphere index on the "location" field in the Stores collection
db.Stores.createIndex({ location: "2dsphere" });

if (user) {
    const userLocation = user.location; // User location
    const userCoordinates = [userLocation.longitude, userLocation.latitude]; // Longitude and latitude as an array

    // Step 3: Query nearby available fresh products 
    const results = db.Stores.aggregate([
        {
            $geoNear: {
                near: {
                    type: "Point",
                    coordinates: userCoordinates // Dynamic user location
                },
                distanceField: "distance", // Field to store the calculated distance
                spherical: true
            }
        },
        {
            $unwind: "$products_available" // Deconstruct the products_available array
        },
        {
            $lookup: {                  // Join the Products collection
                from: "Products", 
                localField: "products_available.product_ID", 
                foreignField: "product_ID", 
                as: "product_details" 
            }
        },
        {
            $unwind: "$product_details" 
        },
        {
            $match: {
                "product_details.product_category": "fresh_product" // Ensure it's a fresh product
            }
        },
        {
            $group: {
                _id: "$store_ID", // Group by Store ID
                store_address: { $first: "$address" }, // Store address
                distance: { $first: { $divide: ["$distance", 1000] } }, // Distance in kilometers
                fresh_products: {
                    $push: {
                        product_name: "$product_details.name", 
                        product_category: "$product_details.fresh_product_details.category", 
                        product_segment: "$product_details.product_segment",
                        product_price: "$product_details.price", 
                        product_quantity: "$products_available.quantity" // Available quantity
                    }
                }
            }
        },
        { $sort: { distance: 1 } }, // Sort by distance in ascending order
        {
            $project: {
                StoreID: "$_id",
                distance: {
                    $concat: [{ $toString: { $round: ["$distance", 2] } }, " km"]
                },
                store_address: 1,
                fresh_products: 1, // Include fresh_products directly
                _id: 0
            }
        }
    ]).toArray(); // Retrieve results as an array
    
    // Output as individual documents
    results.forEach(store => {
        const storeDocument = {
            StoreID: store.StoreID,
            Distance: store.distance,
            Address: store.store_address,
            Products: store.fresh_products
        };
        printjson(storeDocument); 
    });
} else {
    print("User not found"); // Print a message if the user is not found
}
