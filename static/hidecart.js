// Function to hide the show cart section if the cart is empty
function hideShowCart() {
    var cartItems = $('.show-cart tbody tr');
    var showCartSection = $('.show-cart');
    
    if (cartItems.length === 0) {
        showCartSection.fadeOut(100); // Fade out the show cart section
    } else {
        showCartSection.fadeIn(100); // Fade in the show cart section
    }
}

// Call the function to hide/show the show cart section initially
hideShowCart();