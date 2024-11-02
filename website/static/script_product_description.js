document.addEventListener('DOMContentLoaded', () => {
    
    const productTitleBox = document.getElementById('product-title-box');
    const productImage = document.getElementById('product-image');
    const productType = document.getElementById('product-type');
    const productLink = document.getElementById('product-link');
    const productDescription = document.getElementById('product-description');
    
    function loadProductDescription () {
        var productName = window.location.pathname.split('/')[2];
        productImage.src = `/product-images/${productName}`;
        fetch(`/product-descriptions/${productName}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('GET request failed');
                }
                return response.json();
            })
            .then(productData => {
                productTitleBox.innerText = productData.name;
                productType.innerText = productData.category;
                productLink.innerText = productData.link;
                productLink.href = productData.link;
                productDescription.innerText = productData.description;
            })
            .catch(error => {
                console.error(error);
            });
    }

    loadProductDescription();
    
});
