from flask import Flask, request, jsonify
import pymongo
import pandas as pd

app = Flask(__name__)

# Replace these values with your MongoDB connection details
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'recom'
MONGO_COLLECTION = 'ecom'

# Load order data from MongoDB into a pandas DataFrame
def load_order_data():
    client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    cursor = collection.find({})
    df = pd.DataFrame(list(cursor))
    client.close()
    return df

# User-Based Collaborative Filtering recommendation
def get_user_recommendations(user_id, order_data):
    # Check if the user_id exists in the order_data DataFrame
    if user_id not in order_data['user_id'].values:
        print(f"User ID {user_id} not found in the order data.")
        return []

    # Get the list of all product IDs
    all_product_ids = set(order_data['product_id'])

    # Remove the products the user has already ordered
    user_ordered_products = set(order_data[order_data['user_id'] == user_id]['product_id'])
    products_to_recommend = list(all_product_ids - user_ordered_products)

    # Calculate Jaccard similarity between the user and other users
    user_products = set(order_data[order_data['user_id'] == user_id]['product_id'])
    user_similarities = []
    for idx, row in order_data.iterrows():
        if row['user_id'] != user_id:
            other_user_products = set(order_data[order_data['user_id'] == row['user_id']]['product_id'])
            similarity = len(user_products.intersection(other_user_products)) / len(user_products.union(other_user_products))
            user_similarities.append((row['user_id'], similarity))

    # Sort users by similarity in descending order
    user_similarities = sorted(user_similarities, key=lambda x: x[1], reverse=True)

    # Get top N most similar users and their ordered products
    top_n_users = user_similarities[:5]  # You can change this value to get more or fewer similar users
    recommendations = []
    recommended_products = set()
    for other_user_id, similarity in top_n_users:
        other_user_products = set(order_data[order_data['user_id'] == other_user_id]['product_id'])
        for product_id in products_to_recommend:
            if product_id in other_user_products and product_id not in recommended_products:
                # Fetch the product_name from MongoDB
                product_name = order_data[order_data['product_id'] == product_id]['product_name'].values[0]
                recommendations.append((product_id, product_name, similarity))
                recommended_products.add(product_id)

    # Sort product recommendations by user similarity and predicted ratings
    recommendations = sorted(recommendations, key=lambda x: (x[2], x[0]), reverse=True)

    # Return the top N recommended product IDs and product names
    top_n = 5  # You can change this value to get more or fewer recommendations
    top_recommendations = [{'product_id': pid, 'product_name': pname} for pid, pname, _ in recommendations[:top_n]]
    return top_recommendations



@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400

    order_data = load_order_data()
    recommendations = get_user_recommendations(int(user_id), order_data)

    if not recommendations:
        return jsonify({'message': 'User ID not found or no recommendations available.'}), 404

    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
