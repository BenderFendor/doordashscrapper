import re
import redis
from flask import Flask, flash, json, jsonify, render_template, request, redirect, url_for, session
from fuzzywuzzy import fuzz
import csv

from redisearch import Client, TextField, NumericField, Document

r = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # replace with your secret key

# Create a client for the 'items' index
client = Client('items')

# Drop the 'items' index if it exists
try:
    client.info()
    client.drop_index()
except redis.exceptions.ResponseError as e:
    if str(e) != "Unknown Index name":
        print("Index 'items' does not exist, skipping drop_index.")
    else:
        raise  # re-raise the exception if it's something other than "Unknown Index name"

# Create the 'items' index
client.create_index([TextField('item_name'), TextField('price'), TextField('image_url')])

def indexdata():
    data_file_path = 'ACME (2101 Cottman Avenue), Delivered by DoorDash.csv'

    # Load only a subset of the data
    data_list = []

    with open(data_file_path, mode='r', encoding='latin1') as file:
        reader = csv.reader(file)
        headers = next(reader)

        # Check if the index exists
        try:
            client.info()  # This will raise an exception if the index doesn't exist
        except redis.exceptions.ResponseError:
            # Index doesn't exist, create a new one
            client.create_index([TextField('item_name'), TextField('price'), TextField('image_url')])
        else:
            # Index exists, you can choose to drop it or skip the creation step
            print("Index 'items' already exists.")
            # client.drop_index()  # Uncomment this line if you want to drop the existing index

        for i, values in enumerate(reader):
            item = dict(zip(headers, values))
            data_list.append(item)

        for item in data_list:
            keys = ['image_url', 'image_urlpart2', 'image_urlpart3', 'image_urlpart4']
            if all(key in item for key in keys):
                item['image_url'] = ','.join([item[key] for key in keys])
            item['count'] = 1

            # Create a new Redisearch document for each item
            doc_id = item['item_name']
            doc_fields = {
                'item_name': item.get('item_name', 'N/A'),
                'price': item.get('price', 'N/A'),  # use 'N/A' if 'price' key does not exist
                'image_url': item.get('image_url', 'N/A')
            }
            try:
                client.add_document(doc_id, replace=True, **doc_fields)
            except ReferenceError as e:
                if "Document already exists" in str(e):
                    print(f"Document with ID {doc_id} already exists, skipping.")
                else:
                    raise

@app.route('/clear_session')
def clear_session():
    session.clear()
    return "Session cleared"

@app.route('/', defaults={'json_output': False})
@app.route('/data', defaults={'json_output': True}, methods=['GET'])
def showData(json_output):
    data_file_path = 'ACME (2101 Cottman Avenue), Delivered by DoorDash.csv'
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Change this as needed
    offset = (page - 1) * per_page

    # Load only a subset of the data
    data_list = []
    
    with open(data_file_path, mode='r', encoding='latin1') as file:
        reader = csv.reader(file)
        headers = next(reader)
        for i, values in enumerate(reader):
            if i < offset:
                continue
            if i >= offset + per_page:
                break
            item = dict(zip(headers, values))
            data_list.append(item)

        for item in data_list:
            keys = ['image_url', 'image_urlpart2', 'image_urlpart3', 'image_urlpart4']
            if all(key in item for key in keys):
                item['image_url'] = ','.join([item[key] for key in keys])
            else:
                continue
            item['count'] = 1
            
    if json_output:
        return jsonify(data_list)
    else:
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Change this as needed
        offset = (page - 1) * per_page

        # Load only a subset of the data
        data_list = []
        with open(data_file_path, mode='r', encoding='latin1') as file:
            reader = csv.reader(file)
            headers = next(reader)
            for i, values in enumerate(reader):
                if i < offset:
                    continue
                if i >= offset + per_page:
                    break
                item = dict(zip(headers, values))
                data_list.append(item)

       # Store the foodlist in Redis
        r.set('foodlist', json.dumps(data_list))

        # Get the cart from Redis
        foodcart = r.get('cart')
        if foodcart is None:
            foodcart = []
        else:
            foodcart = json.loads(foodcart)

        total_cost = round(sum(float(item['price'].replace('$', '')) * int(item['count']) if item['count'] not in [None, ''] else 0 for item in foodcart if item['price'] is not None), 2)
    
        return render_template('show_csv_data.html', data=data_list, foodcart=foodcart, total_cost=total_cost)

# Define a function to perform fuzzy matching
def fuzzy_match(keyword, item_name):
    threshold = 70  # You can adjust this threshold as per your requirement
    return fuzz.partial_ratio(keyword.lower(), item_name.lower()) >= threshold

@app.route('/update_count', methods=['POST'])
def update_count():
    item_name = request.form.get('item_name')
    count = request.form.get('count')

    # Check if count is a valid number
    if not count.isdigit():
        flash('Count must be a number.')
        return redirect(url_for('showData'))

    # Get data_list from the session
    data_list = session.get('foodlist', [])
    for item in data_list:
        # Check if the item has the key 'item_name'
        if 'item_name' in item and item['item_name'] == item_name:
            item['count'] = int(count)
            break
    else:
        flash('Item not found.')
        return redirect(url_for('showData'))
    
    # Store the updated data_list in the session
    session['foodlist'] = data_list

    # Print the updated cart
    print("Updated cart:", session.get('cart', []))

    # Redirect to the page that shows the items
    return redirect(url_for('showData'))

@app.route('/get_cart')
def get_cart():
    foodcart = session.get('cart', [])
    return jsonify(foodcart)

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []  # Clear the cart by setting it to an empty list
    return jsonify({'status': 'success'})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item_name')
    price = request.form.get('price')
    count = request.form.get('count')
    image_url = request.form.get('image_url')

    # Add the item to the cart
    cart = {
        'item_name': item_name,
        'price': price,
        'image_url': image_url,
        'count': count
    }

    # Get the existing cart from Redis
    foodcart = r.get('cart')
    if foodcart is None:
        foodcart = []
    else:
        foodcart = json.loads(foodcart)

    # Check if the item is already in the cart
    for item in foodcart:
        if item['item_name'] == item_name:
            print("Item already in cart. Updating count.")
            item['count'] = count
            break
    else:
        foodcart.append(cart)

    # Store the updated cart in Redis
    r.set('cart', json.dumps(foodcart))

    return redirect(url_for('showData'))

def updatecart():
    item_name = request.form.get('item_name')
    count = request.form.get('count')

    # Check if count is a valid number
    if not count.isdigit():
        flash('Count must be a number.')
        return redirect(url_for('showData'))

    # Get data_list from the session
    data_list = session.get('foodlist', [])
    for item in data_list:
        # Check if the item has the key 'item_name'
        if 'item_name' in item and item['item_name'] == item_name:
            item['count'] = int(count)
            break
    else:
        flash('Item not found.')
        return redirect(url_for('showData'))
    
    # Store the updated data_list in the session
    session['foodlist'] = data_list

    # Print the updated cart
    print("Updated cart:", session.get('cart', []))

    # Redirect to the page that shows the items
    return redirect(url_for('showData'))

@app.route('/show_cart')
def show_cart():
    foodcart = session.get('cart', [])
        
    print(foodcart)

    if not foodcart:
        return render_template('cart.html', foodcart=foodcart, total_cost=0,is_empty=True)
    
    # this doesn't dyanmically reload the totalcost idk how to do to that

    total_cost = round(sum(float(item['price'].replace('$', '')) * int(item['count']) if item['count'] not in [None, ''] else 0 for item in foodcart if item['price'] is not None), 2)
    return render_template('cart.html', foodcart=foodcart, total_cost=total_cost)

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('query', '')
    print(f"Search query: {search_query}")  # Log the search query
    
    # Sanitize the search query
    search_query = re.sub(r'\W+', '', search_query)
    print(f"Sanitized search query: {search_query}")  # Log the sanitized search query

    # Get information about the RediSearch index
    index_info = client.info()
    print(f"Index info: {index_info}")  # Log the index info

    # Use the RediSearch client to search the 'items' index
    results = client.search(f"{search_query}")  # Perform a prefix search
    # Convert the results to a list of dictionaries
    matched_items = [{field: getattr(doc, field) for field in doc.__dict__.keys()} for doc in results.docs]

    print(f"Search results: {matched_items}")  # Log the search results

    return jsonify(matched_items)  # Return the search results as JSON

@app.route('/get_total_cost')
def get_total_cost():
    foodcart = session.get('cart', [])
    total_cost = round(sum(float(item['price'].replace('$', '')) * int(item['count']) if item['count'] not in [None, ''] else 0 for item in foodcart if item['price'] is not None), 2)
    return jsonify({'total_cost': total_cost})

if __name__ == '__main__':
    indexdata()
    app.run(debug=True)