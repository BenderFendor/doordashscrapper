function addToCart(item_name, price,image_url, count) {
    if (count < 1) {
        count = 1;  
    }
    
    $.ajax({
        type: 'POST',  // Assuming you're making a POST request
        url: '/cart',  // Replace with your actual endpoint
        data: {
            'item_name': item_name,
            'price': price,
            'image_url': image_url,
            'count': count
        },
        success: function(response) {
            console.log('Cart updated:', response.cart)
            console.log('addToCart called with:', item_name, price, image_url, count);
            updateCart();  // Update the cart
        },
        error: function(error) {
            console.error('Error adding item to cart:', error);
        }
        });
    } // Add a closing curly brace here
