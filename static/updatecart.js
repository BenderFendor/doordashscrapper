function updateCart() {
    $.ajax({
        url: '/get_cart',
        type: 'GET',
        success: function(data) {
            var $cart = $('.show-cart tbody');
            $cart.empty();
            $.each(data, function(i, item) {
                var total = item.price * item.quantity;
                var $row = $('<tr>').append(
                    $('<td>').text(item.item_name),
                    $('<td>').text(item.price),
                    $('<td>').text(item.quantity),
                    $('<td>').text(total)
                );
                $cart.append($row);
            });
        }
    });
}