#Requirement 1：At least 2 queries indicating a customer ordering a fresh product. 
The query should include the assignment of pickup and delivery tasks to a partner based on location parameters. 
The query should return, e.g.,  details of the product ordered, delivery partner location and/ or ETA, and details of the delivery partner – name and ratings (if available).

#Query 1: Assign the store, return details of products and stores, and update assignedStore in the Customers collection
db.Customers.aggregate([
    {
      $match: { "current_orders.order_ID": <order_ID> } 
    },
    {
      $unwind: "$current_orders" 
    },
    {
      $match: { "current_orders.order_ID": <order_ID> } 
    },
    {
      $lookup: {
        from: "Products",
        localField: "current_orders.products.product_ID",
        foreignField: "product_ID",
        as: "product_details"
      }
    },
    {
      $lookup: {
        from: "Stores", 
        let: { 
          productID: "$current_orders.products.product_ID", 
          orderQty: "$current_orders.products.quantity" 
        },
        pipeline: [
          { $unwind: "$products_available" }, 
          {
            $match: {
              $expr: {
                $and: [
                  { $eq: ["$products_available.product_ID", "$$productID"] }, 
                  { $gte: ["$products_available.quantity", "$$orderQty"] } //checking the adequacy of stocks
                ]
              }
            }
          }
        ],
        as: "store_details"
      }
    },
    {
      $unwind: "$store_details" 
    },
    {
      $addFields: {
        store_distance: {
          $sqrt: { //calculate the distance between the customer and the store
            $add: [
              { $pow: [{ $subtract: ["$store_details.location.latitude", "$location.latitude"] }, 2] },
              { $pow: [{ $subtract: ["$store_details.location.longitude", "$location.longitude"] }, 2] }
            ]
          }
        }
      }
    },
    {
      $sort: { store_distance: 1 } //sort by distance in ascending order
    },
    {
      $limit: 1 //select the closest store
    },
    {
      $project: {
        "current_orders.order_ID": 1,
        "product_details.fresh_product_details": 1,
        "product_details.description": 1,
        "product_details.product_segment": 1,
        "product_details.product_category": 1,
        "store_details.address": 1,
        "store_details.products_available.quantity": 1,
        "store_details.location.latitude": 1,
        "store_details.location.longitude": 1,
        store_distance: 1
      }
    },
    {
      $merge: {
        into: "Customers",
        whenMatched: "merge",
        let: {
          assignedStore: "$store_details.store_ID"
        },
        whenMatchedPipeline: [
          {
            $set: {
              "current_orders.store_assigned": "$$assignedStore"
            }
          }
        ]
      }
    }
]);

#Query 2: Assign the delivery partner, return partner details and update assignedPartner in the Customers collection
db.Customers.aggregate([
    {
        $match: { "current_orders.order_ID": <order_ID> } 
    },
    {
        $unwind: "$current_orders" 
    },
    {
        $match: { "current_orders.order_ID": <order_ID> } 
    },
    {
        $lookup: {
            from: "Stores",
            localField: "current_orders.store_assigned", // Assigned store from Query 1
            foreignField: "store_ID",
            as: "store_details"
        }
    },
    {
        $unwind: "$store_details" 
    },
    {
        $lookup: {
            from: "Partners", 
            pipeline: [
                {
                    $addFields: {
                        partner_distance: {
                            $sqrt: { // Calculate the distance between the partner and the store
                                $add: [
                                    { $pow: [{ $subtract: ["$current_location.latitude", "$store_details.location.latitude"] }, 2] },
                                    { $pow: [{ $subtract: ["$current_location.longitude", "$store_details.location.longitude"] }, 2] }
                                ]
                            }
                        }
                    }
                },
                { $sort: { partner_distance: 1 } }, // Sort by distance
                { $limit: 1 } // Select the closest partner
            ],
            as: "partner_details"
        }
    },
    {
        $unwind: "$partner_details"
    },
    {
        $project: {
            "current_orders.order_ID": 1,
            "partner_details.name": 1,
            "partner_details.gender": 1,
            "partner_details.age": 1,
            "partner_details.current_location": 1,
            "partner_details.phone": 1,
            "partner_details.delivery_stats.rating": 1,
            partner_distance: 1 
        }
    },
    {
        $merge: {
            into: "Customers",
            whenMatched: "merge",
            let: {
                assignedPartner: "$partner_details.partner_ID"
            },
            whenMatchedPipeline: [
                {
                    $set: {
                        "current_orders.partner_assigned": "$$assignedPartner"
                    }
                }
            ]
        }
    }
]);

#Query 3: Return delivery partner's location and ETA
db.Customers.aggregate([
    {
        $match: { "current_orders.order_ID": <order_ID> } 
    },
    {
        $unwind: "$current_orders" 
    },
    {
        $match: { "current_orders.order_ID": <order_ID> } 
    },
    {
        $lookup: {
            from: "Partners",
            localField: "current_orders.partner_assigned", // Assigned partner from Query 2
            foreignField: "partner_ID",
            as: "partner_details"
        }
    },
    {
        $unwind: "$partner_details"
    },
    {
        $project: {
            "current_orders.order_ID": 1,
            "partner_details.name": 1,
            "partner_details.current_location": 1,
            "partner_details.delivery_stats.rating": 1,
            ETA: {
                $function: {
                    body: function (partnerLoc, customerLoc) {
                        const averageSpeed = 30; // Assuming an average delivery speed of 30 km/h
                        const dLat = customerLoc.latitude - partnerLoc.latitude;
                        const dLon = customerLoc.longitude - partnerLoc.longitude;
                        const distance = Math.sqrt(dLat ** 2 + dLon ** 2); 
                        return Math.ceil((distance / averageSpeed) * 60); // Return ETA in minutes
                    },
                    args: [
                        "$partner_details.current_location", // Partner's location
                        "$location" // Customer's location
                    ],
                    lang: "js"
                }
            }
        }
    }
]);

