function addToCart(item_name, price, image_url, count, store) {
    if (count == undefined) {
        count = 1;  
    }
    
    // Check for undefined values
    if (item_name === undefined || price === undefined || image_url === undefined || store === undefined) {
        console.error('Undefined value detected:', item_name, price, image_url, count, store);
        return;
    }

    $.ajax({
        type: 'POST',  // Assuming you're making a POST request
        url: '/add_to_cart',  // Replace with your actual endpoint
        data: {
            'item_name': item_name,
            'price': price,
            'image_url': image_url,
            'count': count,
            'store': store
        },
        success: function(response) {
            console.log('Response:', response);  // Log the entire response object
            console.log('Cart updated:', response.cart)
            console.log('addToCart called with:', item_name, price, image_url, count, store);
            updateCart(store);  // Update the cart
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('Error adding item to cart:', errorThrown);
            console.error('HTTP status:', jqXHR.status);
            console.error('Status text:', textStatus);
            console.error('Error response:', jqXHR.responseText);

        }
    });
}