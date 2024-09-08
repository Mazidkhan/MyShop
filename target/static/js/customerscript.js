document.addEventListener('DOMContentLoaded', () => {
    const quantityDropdowns = document.querySelectorAll('.quantity-dropdown');
    const totalPriceElement = document.getElementById('total-price');
    const cartRows = document.querySelectorAll('#cart-table tbody tr');

    function updateTotalPrice() {
        console.log('Updating total price...'); // Debugging line
        let totalPrice = 0;

        cartRows.forEach(row => {
            const price = parseFloat(row.dataset.price);
            const discount = parseFloat(row.dataset.discount);
            const dropdown = row.querySelector('.quantity-dropdown');

            if (dropdown) {
                const quantity = parseFloat(dropdown.value);
                const discountedPrice = price - (price * discount / 100);
                totalPrice += discountedPrice * quantity;
            } else {
                console.warn('Dropdown not found in row:', row);
            }
        });

        totalPriceElement.textContent = `Rs.${totalPrice.toFixed(2)}`;
    }

    quantityDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', (event) => {
            const rowIndex = Array.from(dropdown.parentNode.parentNode.parentNode.children).indexOf(dropdown.parentNode.parentNode);
            fetch('http://20.157.92.44/customer/update_quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ index: rowIndex, quantity: dropdown.value })
            }).then(response => {
                if (response.ok) {
                    updateTotalPrice();
                } else {
                    console.error('Failed to update quantity');
                }
            });
        });
    });

    updateTotalPrice();
});
function showForm(formId) {
    document.getElementById(formId).style.display = 'block';
}

function hideForm(event, formId) {
    document.getElementById(formId).style.display = 'none';
}
function addToCart(productId) {
    fetch('http://127.0.0.1:5000/customer/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        alert('Product added to cart!');
    })
    .catch(error => console.error('Error:', error));
}

function changeImage(imageSrc, productId) {
    document.getElementById('mainImage' + productId).src = imageSrc;
}