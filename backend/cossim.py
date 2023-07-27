from flask import Flask, request, jsonify
import pymongo
from surprise import Reader, Dataset, KNNBasic
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
        return []

    # Prepare data for surprise library
    reader = Reader(rating_scale=(0, 1))
    data = Dataset.load_from_df(order_data[['user_id', 'product_id', 'reordered']], reader)

    # Build the training set
    full_trainset = data.build_full_trainset()

    # Filter the trainset to consider only the user's order history
    user_order_data = order_data[order_data['user_id'] == user_id]
    user_data = Dataset.load_from_df(user_order_data[['user_id', 'product_id', 'reordered']], reader)
    user_trainset = user_data.build_full_trainset()

    # Use the KNNBasic algorithm for User-Based Collaborative Filtering with Pearson similarity
    sim_options = {
        'name': 'pearson',
        'user_based': True
    }
    knn = KNNBasic(sim_options=sim_options)
    knn.fit(user_trainset)

    # Get the list of all product IDs
    all_product_ids = set(order_data['product_id'])

    # Remove the products the user has already ordered
    user_ordered_products = set(order_data[order_data['user_id'] == user_id]['product_id'])
    products_to_recommend = list(all_product_ids - user_ordered_products)

    # Predict the ratings for products that the user hasn't ordered
    recommendations = []
    for product_id in products_to_recommend:
        try:
            predicted_rating = knn.predict(user_id, product_id).est

            # Fetch the product_name from MongoDB
            product_name = order_data[order_data['product_id'] == product_id]['product_name'].values[0]

            recommendations.append((product_id, product_name, predicted_rating))
        except:
            # If no rating is available for a user-product pair, continue to the next product
            continue

    # Combine product IDs with their predicted ratings and sort by ratings
    recommendations = sorted(recommendations, key=lambda x: x[2], reverse=True)

    # Return the top N recommended product IDs and product names
    top_n = 5
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