function updateStatus(orderID) {
    const dropdown = document.querySelector(`.status-dropdown[data-order-id="${orderID}"]`);
    const selectedStatus = dropdown.value;

    const data = {
        status: selectedStatus
    };

    // Send data to server
    fetch(`/delivery/update-order-status/${orderID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Order status updated successfully!') {
            alert('Order status updated successfully!');
            location.reload(); // Refresh the page to reflect the changes
        } else {
            alert('Failed to update order status.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the order status.');
    });
}

function closePopup() {
    document.getElementById('popupForm').style.display = 'none';
}

function fetchOrderDetails() {
    console.log("Button clicked!"); // Add this line to check
    var orderID = document.getElementById('order_id').value;

    fetch('/delivery/get-order-details/' + orderID)
    .then(response => response.json())
    .then(data => {
        console.log("Data received:", data); // Log data to verify it's received

        // Clear previous order details
        var orderDetailsBody = document.getElementById('orderDetailsBody');
        orderDetailsBody.innerHTML = '';

        // Populate order details in the table
        data.forEach(item => {
            var row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.product_name}</td>
                <td>${item.product_brand}</td>
                <td>${item.quantity}</td>
                <td>${item.price}</td>
                <td>${item.quantity * item.price}</td>
            `;
            orderDetailsBody.appendChild(row);
        });

        // Display the popup
        document.getElementById('popupForm').style.display = 'flex';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while fetching order details.');
    });
}
