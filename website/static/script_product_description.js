document.addEventListener('DOMContentLoaded', () => {
    
    const playButton = document.getElementById('start-guessing-button');
    playButton.href = window.location.pathname + '/guess';
    
    const productTitleBox = document.getElementById('product-title-box');
    const productImage = document.getElementById('product-image');
    const productType = document.getElementById('product-type');
    const productLink = document.getElementById('product-link');
    const productDescription = document.getElementById('product-description');
    
    function loadProductDescription() {
        var categoryName = window.location.pathname.split('/')[1];
        var url = '/product-description?' + new URLSearchParams({
            category: categoryName
        }).toString();
        fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('GET request failed');
            }
            return response.json();
        })
        .then(productData => {
            productTitleBox.innerText = productData.name;
            productImage.src = productData.image;
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
