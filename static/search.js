document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the form from being submitted normally

    var searchQuery = document.getElementById('search').value;  // Get the search query

    console.log('Search query:', searchQuery)
    console.log('Full URL with encoded search query:', 'http://localhost:5000/search?search=' + encodeURIComponent(searchQuery));
    // Send an AJAX request to the server
    fetch('/search?search=' + encodeURIComponent(searchQuery), {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data:', data);
        // Get all items
        let allItems = document.querySelectorAll('.allitems > div');

        // Convert the NodeList to an array and loop through each item
        Array.from(allItems).forEach(item => {
            // Show all items to reset search
            item.style.display = 'block';
            // Get the item name from the h2.itemname element's text content
            let itemName = item.querySelector('.itemname').textContent;

            // Check if the item is in the data
            let itemInData = data.some(dataItem => dataItem.item_name === itemName);

            // If the item is not in the data, hide it
            if (!itemInData) {
                item.style.display = 'none';
            }
            
            // If no items were found, show a message
            if (data.length === 0) {
                document.getElementById('no-items-found').style.display = 'block';
                document.getElementById('no-items-found').textContent = 'No items found that matched with the search query ' + searchQuery;
            }
        });
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});