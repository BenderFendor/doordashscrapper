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

            function updateTotalCost() {
                $.ajax({ 
                    url: '/get_total_cost',
                    type: 'GET',
                    success: function(data) {
                        $('#total-cost').text("The Total Cost Of This Cart is $" + data.total_cost);
                        console.log('Total cost:', data.total_cost);
                    }
                });
            }
            
            updateTotalCost();
            hideShowCart();
        }
    });
}