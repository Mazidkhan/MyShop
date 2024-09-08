document.getElementById('addButton').onclick = function() {
    document.getElementById('popupForm').style.display = 'flex';
}

document.getElementsByClassName('close')[0].onclick = function() {
    document.getElementById('popupForm').style.display = 'none';
}

window.onclick = function(event) {
    if (event.target == document.getElementById('popupForm')) {
        document.getElementById('popupForm').style.display = 'none';
    }
}

function submitForm(event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(document.getElementById('deliveryBoyForm'));
    const data = {
        boy: formData.get('boy'),
        phone: formData.get('phone'),
        email: formData.get('email'),
        password: formData.get('password')
    };

    fetch('http://127.0.0.1:5000/admin/add_delivery_boy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            alert('Delivery boy added successfully!');
            document.getElementById('popupForm').style.display = 'none'; // Close the popup
            // Optionally, you could also refresh the table or perform other UI updates here
        } else {
            alert('Error adding delivery boy.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the delivery boy.');
    });
}

function showPopup() {
    document.getElementById('registerPopup').style.display = 'flex';
}

// Function to close the popup
function closePopup() {
    document.getElementById('registerPopup').style.display = 'none';
}

// Close the popup if the user clicks outside of it
window.onclick = function(event) {
    if (event.target == document.getElementById('registerPopup')) {
        closePopup();
    }
}

    // Get the modal
    var modal = document.getElementById("assignOrderModal");

    // Get the button that opens the modal
    var btn = document.getElementById("assignOrderBtn");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks the button, open the modal
    btn.onclick = function() {
        modal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // Populate the Order ID dropdown with values from the database
    document.addEventListener('DOMContentLoaded', function() {
        fetch('http://127.0.0.1:5000/admin/get_order_ids') // Flask route to fetch order IDs
        .then(response => response.json())
        .then(data => {
            var select = document.getElementById('orderId');
            if (data.order_ids && Array.isArray(data.order_ids)) {
                data.order_ids.forEach(function(orderId) {
                    var option = document.createElement('option');
                    option.value = orderId;
                    option.text = orderId;
                    select.appendChild(option);
                });
            } else {
                console.error('Invalid data format:', data);
            }
        })
        .catch(error => {
            console.error('Error fetching order IDs:', error);
        });
    });

    // Handle form submission
    document.getElementById('assignOrderForm').addEventListener('submit', function(e) {
        e.preventDefault();

        var orderId = document.getElementById('orderId').value;
        var deliveryBoy = document.getElementById('deliveryBoy').value;

        if (orderId && deliveryBoy) {
            fetch('http://127.0.0.1:5000/admin/assign_order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    orderId: orderId,
                    deliveryBoy: deliveryBoy
                })
            })
            .then(response => {
                if (response.ok) {
                    alert('Order assigned successfully!');
                    modal.style.display = "none";
                } else {
                    alert('Failed to assign order.');
                }
            })
            .catch(error => {
                console.error('Error assigning order:', error);
            });
        } else {
            alert('Please select an order ID and enter a delivery boy name.');
        }
    });
    // Filter orders by status
document.getElementById('filterStatusBtn').addEventListener('click', function() {
    var selectedStatus = document.getElementById('orderStatus').value;

    // Fetch and filter orders based on the selected status
    fetch('http://127.0.0.1:5000/admin/filter_orders?status=' + selectedStatus)
    .then(response => response.json())
    .then(data => {
        var tbody = document.querySelector('table tbody');
        tbody.innerHTML = ''; // Clear existing rows

        data.orders.forEach(function(order) {
            var row = document.createElement('tr');

            row.innerHTML = `
                <td>${order.id}</td>
                <td>${order.customer_name}</td>
                <td>${order.product_name}</td>
                <td>${order.product_category}</td>
                <td>${order.product_brand}</td>
                <td>${order.quantity}</td>
                <td>$${order.price}</td>
                <td>$${order.total_price}</td>
                <td>${order.date}</td>
                <td>${order.status}</td>
            `;

            tbody.appendChild(row);
        });
    })
    .catch(error => {
        console.error('Error fetching orders:', error);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var openFormButton = document.getElementById('openFormButton');
    var popupForm = document.getElementById('popupForm');
    var closeFormButton = document.getElementById('closeFormButton');

    openFormButton.addEventListener('click', function() {
        popupForm.style.display = 'flex';
    });

    closeFormButton.addEventListener('click', function() {
        popupForm.style.display = 'none';
    });

    // Close edit form popup
    var closeEditFormButton = document.getElementById('closeEditFormButton');
    var editFormPopup = document.getElementById('editFormPopup');

    closeEditFormButton.addEventListener('click', function() {
        editFormPopup.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target == popupForm) {
            popupForm.style.display = 'none';
        } else if (event.target == editFormPopup) {
            editFormPopup.style.display = 'none';
        }
    });

    // Event listeners for edit and delete buttons
    document.querySelectorAll('.edit-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var id = this.getAttribute('data-id');
            fetch(`http://127.0.0.1:5000/admin/product/${id}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('Product not found!');
                        return;
                    }
                    document.getElementById('editProductId').value = data.id;
                    document.getElementById('editProductName').value = data.product_name;
                    document.getElementById('editProductBrand').value = data.product_brand;
                    document.getElementById('editProductCategory').value = data.product_category;
                    document.getElementById('editProductPrice').value = data.price;
                    document.getElementById('editProductDiscount').value = data.discount;
                    document.getElementById('editProductStock').value = data.stock;
                    // Pre-fill images if needed (optional, depending on how you handle images)
                    editFormPopup.style.display = 'flex';
                });
        });
    });

    document.querySelectorAll('.delete-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var id = this.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this product?')) {
                fetch(`http://127.0.0.1:5000/admin/delete_product/${id}`, {
                    method: 'DELETE',
                })
                .then(response => {
                    if (response.ok) {
                        // Remove the row from the table
                        button.closest('tr').remove();
                        alert('Product deleted successfully!');
                    } else {
                        alert('Failed to delete product.');
                    }
                });
            }
        });
    });

    document.getElementById('editProductForm').addEventListener('submit', function(event) {
        event.preventDefault();

        var formData = new FormData(this);

        fetch('http://127.0.0.1:5000/admin/update_product', {
            method: 'PUT',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                alert('Product updated successfully!');
                location.reload(); // Reload to reflect changes
            } else {
                alert('Failed to update product.');
            }
        });
    });
});
