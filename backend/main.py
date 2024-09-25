from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from flask_cors import CORS 

app = Flask(__name__)

CORS(app)
# MongoDB Configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['supplier_database']
collection = db['supplier_data']
collectionSubForCost = db['supplier_data_for_cost']

# Index route to render HTML form
@app.route('/')
def index():
    return render_template('index.html')

# API to handle POST request and save data to MongoDB
@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Get JSON data from the request
        supplier_data = request.json

        # Ensure all required fields are present
        if not supplier_data or 'supplier_name' not in supplier_data or 'product_info' not in supplier_data:
            return jsonify({"status": "error", "message": "Missing required fields."}), 400

        # Prepare the supplier data to be inserted
        supplier_data = {
            "supplier_name": supplier_data.get('supplier_name'),
            "product_info": supplier_data.get('product_info'),
            "website_url": supplier_data.get('website_url'),
            "category": supplier_data.get('category'),
            "quantity_required": int(supplier_data.get('quantity_required', 0)),  # Default to 0 if not provided
            "timeline": supplier_data.get('timeline'),
            "location": supplier_data.get('location'),
            "required_for": supplier_data.get('required_for'),
            "submitted_at": datetime.now()  # Optional: Store timestamp
        }

        # Insert data into MongoDB
        inserted_id = collection.insert_one(supplier_data).inserted_id

        return jsonify({"status": "success", "inserted_id": str(inserted_id)}), 201  # HTTP 201 Created

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500  # Internal Server Error


@app.route('/get_products', methods=['POST'])
def get_products():
    # Parse the request body for filter criteria (if any)
    request_data = request.get_json()
    
    # Optional: Use filters if you want to query specific data
    # For example, you could filter by category or product name if needed
    filters = []
    if 'category' in request_data:
        filters.append({"category": request_data['category']})

    # Check if 'product_info' is in the request data
    if 'product_info' in request_data:
        filters.append({"product_info": {"$regex": request_data['product_info'], "$options": "i"}})  # case-insensitive search

    # Build the query
    if filters:
        query = {"$or": filters}  # Only use $or if filters are present
    else:
        query = {} 
    # Fetch product details from MongoDB (filter based on user input if provided)
    products = collectionSubForCost.find(query, {'_id': 0, 'product_info': 1, 'category': 1, 'cost': 1,'image':1})
    
    # Convert the cursor to a list of dictionaries
    product_list = list(products)
    
    # Return the data as JSON response
    return jsonify(product_list)




@app.route('/sample_products', methods=['POST'])
def addProductWithCost():
    if request.method == 'POST':
        supplier_data = {
            "product_info": request.form.get('product_info'),
            "category": request.form.get('category'),
            "cost":request.form.get('cost'),
            "image":request.form.get('image')
         }

        # Insert data into MongoDB
        inserted_id = collectionSubForCost.insert_one(supplier_data).inserted_id

        return jsonify({"status": "success", "inserted_id": str(inserted_id)})




if __name__ == '__main__':
    app.run(debug=True)
