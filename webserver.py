from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
from fuzzywuzzy import fuzz
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # replace with your secret key

data_list = []

@app.route('/clear_session')
def clear_session():
    session.clear()
    return "Session cleared"

@app.route('/')
def showData():
    session['foodlist'] = []
    # read csv
    data_file_path = 'testdoordashoutput.csv'
    global data_list
    data_list = []
    with open(data_file_path, mode='r', encoding='latin1') as file:
        reader = csv.reader(file)
        headers = next(reader)
        for values in reader:
            item = dict(zip(headers, values))
            data_list.append(item)
    
    for item in data_list:
        item['image_url'] = ','.join([item['image_url'], item['image_urlpart2'], item['image_urlpart3'], item['image_urlpart4']])

    # Store data_list in the session
    session['foodlist'] = data_list
    if session.get('foodlist') is None:
        print("Session is empty")
    else:
        print("Session is not empty")

    if data_list:
        first_item = data_list[0]
        print(f"First item: Name={first_item['item_name']}, Price={first_item['price']}, Cost={first_item['image_url']}")

    # Get cart data from the session
    foodcart = session.get('cart', [])
    
    total_cost = sum(float(item['price'].replace('$', '')) * int(item['count']) if item['count'] not in [None, ''] else 0 for item in foodcart if item['price'] is not None)

    return render_template('show_csv_data.html', data=data_list,foodcart=foodcart,total_cost = total_cost)

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

    print(f"Added item to cart: Name={item_name}, Price={price}, Count={count}")
    
    # Get the existing cart from the session
    foodcart = session.get('cart', [])

    # Check if the item is already in the cart
    for item in foodcart:
        if item['item_name'] == item_name:
            print("Item already in cart. Updating count.")
            item['count'] = count
            break
    else:
        # If the item is not in the cart, add it
        foodcart.append(cart)
        
    session['cart'] = foodcart

    # Print the updated cart
    print("Updated cart:", session.get('cart', []))

    # Redirect to the page that shows the cart
    return jsonify({'cart': foodcart})

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
    if not foodcart:
        return render_template('cart.html', foodcart=foodcart, total_cost=0,is_empty=True)
    
    total_cost = sum(float(item['price'].replace('$', '')) * int(item['count']) if item['count'] not in [None, ''] else 0 for item in foodcart if item['price'] is not None)['price'] is not None
    return render_template('cart.html', foodcart=foodcart, total_cost=total_cost)

@app.route('/search', methods=['GET'])
def search():
    global data_list
    search_query = request.args.get('search', '')  # Get the search query from the URL parameters

    print(data_list)

    # Use the fuzzy_match function to filter the data_list
    matched_items = [item for item in data_list if fuzzy_match(search_query, item['item_name'])]

    return jsonify(matched_items)  # Return the search results as JSON

if __name__ == '__main__':
    app.run(debug=True)