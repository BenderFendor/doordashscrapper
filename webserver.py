import re
import redis
from flask import Flask, flash, json, jsonify, render_template, request, redirect, url_for, session
from thefuzz import fuzz,process
import csv
import os
import numpy as np

from redisearch import Client, TextField, NumericField, Document,Query
from redis import Redis, ResponseError


def create_app():

    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # replace with your secret key

    r = redis.Redis(host='localhost', port=6379, db=0)
    
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
    client.create_index([TextField('item_name'), TextField('price'), TextField('image_url'), TextField('store'), NumericField('count')])

    def get_csv_files():
        csv_files = [f for f in os.listdir() if f.endswith(".csv")]
        print(f"Found CSV files: {csv_files}")
        return csv_files

    @app.route('/get_current_csv')
    def get_current_csv():
        csvfiles = get_csv_files()
        return jsonify({'current_csv': csvfiles})

    def read_csv(data_file_path, store=None):
        data_list = []

        if store is None:
            store = format(data_file_path.replace('.csv', ''))

        with open(data_file_path, mode='r', encoding='latin1') as file:
            reader = csv.reader(file)
            headers = next(reader)
            for values in reader:
                item = dict(zip(headers, values))
                keys = ['image_url', 'image_urlpart2', 'image_urlpart3', 'image_urlpart4']
                if all(key in item for key in keys):
                    item['image_url'] = ','.join([item[key] for key in keys])
                else:
                    continue
                item['count'] = 1
                item['store'] = store
                data_list.append(item)

        return data_list

    def index_data(csvfile=None):
        csvfiles = get_csv_files()
        if csvfile is None:
            csvfile = csvfiles[0]

        data_file_path = csvfile

        data_list = read_csv(data_file_path)

        try:
            client.info()  # This will raise an exception if the index doesn't exist
        except redis.exceptions.ResponseError:
            # Index doesn't exist, create a new one
            client.create_index([TextField('item_name'), TextField('price'), TextField('image_url'), TextField('store'), NumericField('count')])
        else:
            # Index exists, you can choose to drop it or skip the creation step
            print("Index 'items' already exists.")
            client.drop_index()  # Uncomment this line if you want to drop the existing index
            client.create_index([TextField('item_name'), TextField('price'), TextField('image_url'), TextField('store'), NumericField('count')])

        for item in data_list:
            doc_id = item['item_name']
            doc_fields = {
                'item_name': item.get('item_name', 'N/A'),
                'price': item.get('price', 'N/A'),  # use 'N/A' if 'price' key does not exist
                'image_url': item.get('image_url', 'N/A'),
                'store': item.get('store', 'N/A'),
                'count': item.get('count', 1)  # use 1 if 'count' key does not exist
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
        # Clear the Redis database
        r.flushdb()
        session.clear()
        return "Session cleared"

    @app.route('/', defaults={'json_output': False})
    @app.route('/data', defaults={'json_output': True}, methods=['GET'])
    def show_data(json_output):
        store = request.args.get('store')
        csvfiles = get_csv_files()

        if not csvfiles:
            print("No CSV files found")
            return render_template('error.html', message="No CSV files found"), 404

        csvfile = request.args.get('csvfile')
        if csvfile is None:
            csvfile = csvfiles[0]

        if csvfile not in csvfiles:
            print(f"CSV file '{csvfile}' not found")
            return render_template('error.html', message=f"CSV file '{csvfile}' not found"), 404

        current_csv = session.get('current_csv')
        if csvfile != current_csv:
            index_data(csvfile)
            session['current_csv'] = csvfile

        page = request.args.get('page', 1, type=int)
        per_page = 40  # Change this as needed
        offset = (page - 1) * per_page

        data_list = read_csv(csvfile, store)
        data_subset = data_list[offset:offset + per_page]

        if json_output:
            return jsonify(data_subset)
        else:
            foodcart = get_cart_from_redis()
            total_cost = round(sum(float(item['price'].replace('$', '')) * int(item['count']) if item['count'] not in [None, ''] else 0 for item in foodcart if item['price'] is not None), 2)
            return render_template('show_csv_data.html', data=data_subset, foodcart=foodcart, total_cost=total_cost, csvfiles=csvfiles)

    @app.route('/update_count', methods=['POST'])
    def update_count():
        item_name = request.form.get('item_name')
        count = request.form.get('count')

        # Check if count is a valid number
        if not count.isdigit():
            flash('Count must be a number.')
            return redirect(url_for('show_data'))

        foodcart = get_cart_from_redis()
        for item in foodcart:
            if item['item_name'] == item_name:
                item['count'] = int(count)
                break
        else:
            flash('Item not found.')
            return redirect(url_for('show_data'))

        store_cart_in_redis(foodcart)

        return redirect(url_for('show_data'))

    @app.route('/get_cart')
    def get_cart():
        foodcart = get_cart_from_redis()
        return jsonify(foodcart)

    @app.route('/clear_cart')
    def clear_cart():
        r.delete('cart')
        return jsonify({'status': 'success'})

    @app.route('/add_to_cart', methods=['POST'])
    def add_to_cart():
        item = {
            'item_name': request.form.get('item_name'),
            'price': request.form.get('price'),
            'image_url': request.form.get('image_url'),
            'count': request.form.get('count'),  # Make sure to convert 'count' to an integer
            'store': request.form.get('store')
        }

        

        foodcart = get_cart_from_redis()

        for existing_item in foodcart:
            if existing_item['item_name'] == item['item_name']:
                print("Item already in cart. Updating count.")
                existing_item['count'] = item['count']
                break
        else:
            foodcart.append(item)

        store_cart_in_redis(foodcart)

        return jsonify(cart=foodcart)
    
    def get_cart_from_redis():
        foodcart = r.get('cart')
        return json.loads(foodcart) if foodcart else []

    def store_cart_in_redis(cart):
        r.set('cart', json.dumps(cart))

    @app.route('/show_cart')
    def show_cart():
        foodcart = get_cart_from_redis()

        if not foodcart:
            return render_template('cart.html', foodcart=foodcart, is_empty=True)
        else:
            return render_template('cart.html', foodcart=foodcart)

    @app.route('/search', methods=['GET'])
    def search():
        search_query = request.args.get('query', '')
        print(f"Search query: {search_query}")  # Log the search query

        # Sanitize the search query
        search_query = re.sub(r'\W+', '', search_query)
        print(f"Sanitized search query: {search_query}")  # Log the sanitized search query

        # Use the RediSearch client to search the 'items' index
        results = client.search(f"{search_query}")  # Perform a prefix search
        # Convert the results to a list of dictionaries
        matched_items = [{field: getattr(doc, field) for field in doc.__dict__.keys()} for doc in results.docs]

        print(f"Search results: {matched_items}")  # Log the search results

        return jsonify(matched_items)  # Return the search results as JSON

    @app.route('/get_total_cost')
    def get_total_cost():
        foodcart = get_cart_from_redis()
        total_cost = round(sum(float(item['price'].replace('$', '')) * int(item['count']) if item['count'] not in [None, ''] else 0 for item in foodcart if item['price'] is not None), 2)
        return jsonify({'total_cost': total_cost})

    @app.route('/compare_carts')
    def compare_carts():
        # Get the current cart from Redis
        current_cart = get_cart_from_redis()
        print(f"Current cart: {current_cart}")

        # Convert the current cart to a set of tuples for efficient lookup
        current_cart_set = set((item['item_name'], item['store']) for item in current_cart)

        # Calculate the similarity score for each unique item in the current cart
        similarity_scores = []

        for csvfile in get_csv_files():
            if csvfile == session.get('current_csv'):
                print(f"Skipping current CSV file: {csvfile}")
                continue

            other_cart = read_csv(csvfile)
            print(f"Other cart: {other_cart}")

            matched_items = set()
            for other_item in other_cart:
                other_item_key = (other_item['item_name'], other_item['store'])
                for current_item_key in current_cart_set:
                    if current_item_key not in matched_items:
                        similarity_score = fuzz.partial_token_sort_ratio(other_item_key, current_item_key)
                        if similarity_score > 75:  # adjust the threshold as needed
                            # Find the current_item that matches current_item_key
                            current_item = next((item for item in current_cart if (item['item_name'], item['store']) == current_item_key), None)
                            if current_item is not None:
                                similarity_score = process.extractOne(current_item['item_name'], [other_item['item_name']], scorer=fuzz.partial_token_sort_ratio)[1]
                                if similarity_score is not None:  # Only append if the score is not None
                                    similarity_scores.append((current_item, other_item, similarity_score))
                                    matched_items.add(current_item_key)  # Add the current_item_key to the matched_items set
            
        print(f"Similarity scores: {similarity_scores}")

        # Sort the similarity scores in descending order
        similarity_scores.sort(key=lambda x: x[2], reverse=True)

        return jsonify({'similarity_scores': similarity_scores})

    index_data()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)