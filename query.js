// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

// The current database to use.
use("DATABASE");

// Step 1: Retrieve user information and location
const user = db.Customer.findOne({ _id: 1 }); // Assuming the user ID is 1

// Step 2: Create a 2dsphere index on the "location" field in the Stores collection
db.Stores.createIndex({ location: "2dsphere" });

if (user) {
    const userLocation = user.location; // User location
    const userCoordinates = [userLocation.longitude, userLocation.latitude]; // Longitude and latitude as an array

    // Step 3: Query nearby available fresh products 
    db.Stores.aggregate([
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
                foreignField: "_id", 
                as: "product_details" 
            }
        },
        {
            $unwind: "$product_details" 
        },
        {
            $match: {
                "product_details.product_segment": "Fresh" // Filter fresh products
            }
        },
        {
            $group: {
                _id: "$_id", // Group by Store ID
                store_address: { $first: "$address" }, // Store address
                distance: { $first: { $divide: ["$distance", 1000] } }, // Distance in kilometers
                fresh_products: {
                    $push: {
                        product_name: "$product_details.name", 
                        product_category: "$product_details.product_category", 
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
                    $concat: [{ $toString: { $round: ["$distance", 2] } }, "km"]
                },
                store_address: 1,
                fresh_products: {
                    $map: {
                        input: "$fresh_products",
                        as: "product",
                        in: {
                            product_name: "$$product.product_name",
                            product_category: "$$product.product_category",
                            product_price: {
                                $concat: [
                                    { $toString: "$$product.product_price" },
                                    " £"
                                ]
                            },
                            product_quantity: "$$product.product_quantity"
                        }
                    }
                },
                _id: 0
            }
        }
        
    ]).forEach(printjson); 
} else {
    print("User not found"); // Print a message if the user is not found
}

