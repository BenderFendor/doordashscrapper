function updateCart() {
    $.ajax({ 
        url: '/get_cart',
        type: 'GET',
        success: function(data) {
                if (data.status === 'success') 
                {
                    updateCart();  // Update the cart
                }
            var $cart = $('.show-cart tbody');
            $cart.empty(); // add it so that it updates the total as well
            $.each(data, function(i, item) {
                var total = item.price * item.count;
                var $row = $('<tr>').append(
                    $('<td>').text(item.item_name),
                    $('<td>').text(item.price),
                    $('<td>').text(item.count),
                );
                $cart.append($row);
            });
        }
    });
}