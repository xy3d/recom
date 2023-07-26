from flask import Flask, request, jsonify
import pymongo
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

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

# Load product data from MongoDB into a pandas DataFrame
def load_product_data():
    client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    cursor = collection.find({}, {'product_id': 1, 'product_name': 1, 'product_description': 1, 'department': 1})
    df = pd.DataFrame(list(cursor))
    client.close()
    return df

# Content-Based Filtering recommendation
def get_user_recommendations(user_id, order_data, product_data):
    # Check if the user_id exists in the order_data DataFrame
    if user_id not in order_data['user_id'].values:
        print(f"User ID {user_id} not found in the order data.")
        return []

    # Get the list of all product IDs
    all_product_ids = set(order_data['product_id'])

    # Remove the products the user has already ordered
    user_ordered_products = set(order_data[order_data['user_id'] == user_id]['product_id'])
    products_to_recommend = list(all_product_ids - user_ordered_products)

    # Create a TF-IDF vectorizer to convert product descriptions into numerical vectors
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    product_tfidf_matrix = tfidf_vectorizer.fit_transform(product_data['department'].fillna(''))

    # Calculate similarity between the user and all products based on their descriptions
    user_tfidf_vector = product_tfidf_matrix[product_data[product_data['product_id'].isin(user_ordered_products)].index]
    product_similarities = linear_kernel(user_tfidf_vector, product_tfidf_matrix)

    # Generate content-based recommendations for the user
    recommendations = []
    for product_id in products_to_recommend:
        product_idx = product_data[product_data['product_id'] == product_id].index[0]
        similarity_score = product_similarities[0, product_idx]

        # Fetch the product_name from MongoDB
        product_name = product_data.iloc[product_idx]['product_name']
        recommendations.append((product_id, product_name, similarity_score))

    # Sort product recommendations by similarity
    recommendations = sorted(recommendations, key=lambda x: x[2], reverse=True)

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
    product_data = load_product_data()
    recommendations = get_user_recommendations(int(user_id), order_data, product_data)

    if not recommendations:
        return jsonify({'message': 'User ID not found or no recommendations available.'}), 404

    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
