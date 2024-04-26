function clearCart() {
    $.ajax({
        url: '/clear_cart',
        type: 'GET',
        success: function(data) {
            if (data.status === 'success') {
                updateCart();  // Update the cart
            }
        }
    });
}