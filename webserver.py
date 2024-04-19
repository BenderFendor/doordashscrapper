from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
from fuzzywuzzy import fuzz
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # replace with your secret key

@app.route('/clear_session')
def clear_session():
    session.clear()
    return "Session cleared"

@app.route('/')
def showData():
    # read csv
    data_file_path = 'testdoordashoutput.csv'
    data_list = []
    with open(data_file_path, mode='r', encoding='latin1') as file:
        lines = file.readlines()
        headers = lines[0].strip().split(',')
        for line in lines[1:]:
            values = line.strip().split(',')
            item = dict(zip(headers, values))
            data_list.append(item)
    
    for item in data_list:
        item['image_url'] = ','.join([item['image_url'], item['image_urlpart2'], item['image_urlpart3'], item['image_urlpart4']])
        item['count'] = 0

    # Store data_list in the session
    session['foodlist'] = data_list

    if data_list:
        first_item = data_list[0]
        print(f"First item: Name={first_item['item_name']}, Price={first_item['price']}, Cost={first_item['image_url']}")
    
    return render_template('show_csv_data.html', data=data_list)

# Define a function to perform fuzzy matching
def fuzzy_match(keyword, item_name):
    threshold = 70  # You can adjust this threshold as per your requirement
    return fuzz.ratio(keyword.lower(), item_name.lower()) >= threshold

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form.get('keyword')

    # Get data_list from the session
    data_list = session.get('cart', [])

    print(data_list)

    return render_template('show_csv_data.html')#,data=filtered_data)

@app.route('/update_count', methods=['POST'])
def update_count():
    item_name = request.form.get('item_name')
    count = request.form.get('count')

    # Check if count is a valid number
    if not count.isdigit():
        flash('Count must be a number.')
        return redirect(url_for('showData'))

    # Get data_list from the session
    data_list = session.get('cart', [])
    for item in data_list:
        # Check if the item has the key 'item_name'
        if 'item_name' in item and item['item_name'] == item_name:
            item['count'] = int(count)
            break
    else:
        flash('Item not found.')
        return redirect(url_for('showData'))
    
    # Store the updated data_list in the session
    session['cart'] = data_list

    # Print the updated cart
    print("Updated cart:", session.get('cart', []))

    # Redirect to the page that shows the items
    return redirect(url_for('showData'))

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
    return redirect(url_for('show_cart'))

@app.route('/show_cart')
def show_cart():
    foodcart = session.get('cart', [])
    total_cost = sum(float(item['price'].replace('$', '')) * int(item['count']) for item in foodcart)
    print("Total cost:", total_cost)
    return render_template('cart.html', foodcart=foodcart, total_cost=total_cost)

if __name__ == '__main__':
    app.run(debug=True)