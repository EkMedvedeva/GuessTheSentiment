document.addEventListener('DOMContentLoaded', async () => {
    
    const playButton = document.getElementById('navigation-start');
    playButton.href = window.location.pathname + '/guess';
    
    const productTitleBox = document.getElementById('product-title-box');
    const productImage = document.getElementById('product-image');
    const productType = document.getElementById('product-type');
    const productLink = document.getElementById('product-link');
    const productDescription = document.getElementById('product-description');
    
    const categoryName = window.location.pathname.split('/')[1];
    const userName = localStorage.getItem('userName');
    
    try {
        let response = await fetch('/session/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: userName,
                category: categoryName
            })
        });
        
        if (!response.ok) {
            throw new Error('POST request failed');
        }
        
        const sessionData = await response.json();
        const productName = sessionData.product;
        
        productImage.src = '/product/image?' + new URLSearchParams({
            product: productName
        }).toString();
        
        let url = '/product/description?' + new URLSearchParams({
            product: productName
        }).toString();
        response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('GET request failed');
        }
        const productData = await response.json();
        
        productTitleBox.innerText = productData.name;
        productType.innerText = productData.category;
        productLink.innerText = productData.link;
        productLink.href = productData.link;
        productDescription.innerText = productData.description;
        
    } catch (error) {
        console.error(error);
        return;
    }
    
});
