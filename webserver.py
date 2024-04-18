from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # replace with your secret key

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
    session['cart'] = data_list

    if data_list:
        first_item = data_list[0]
        print(f"First item: Name={first_item['item_name']}, Price={first_item['price']}, Cost={first_item['image_url']}")
    
    return render_template('show_csv_data.html', data=data_list)

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

    # Add the item to the cart (this will depend on how your cart is implemented)
    cart = {
        'item_name': item_name,
        'price': price,
        'count': count
    }

    print(f"Added item to cart: Name={item_name}, Price={price}, Count={count}")
    
    # Get the existing cart from the session, add the new item to it, and store it back in the session
    foodcart = session.get('cart', [])
    foodcart.append(cart)
    session['cart'] = foodcart

    # Print the updated cart
    print("Updated cart:", session.get('cart', []))

    # Redirect to the page that shows the cart
    return redirect(url_for('show_cart'))

@app.route('/cart')
def show_cart():
    print(session.get('foodcart', []))
    return render_template('cart.html', cart=session.get('foodcart', []))

if __name__ == '__main__':
    app.run(debug=True)