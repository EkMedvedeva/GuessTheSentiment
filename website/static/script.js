document.addEventListener('DOMContentLoaded', () => {
    const playButton = document.getElementById('play-button');
    const rateButton = document.getElementById('rate-button');
    const product = document.getElementById('product');
    const productDescription = document.getElementById('product-description');
    const review = document.getElementById('review');
    const ratingSlider = document.getElementById('rating');
    const sliderValue = document.getElementById('slider-value');
    
    const adminCheckButton = document.getElementById('admin-check-button');
    const adminDeployButton = document.getElementById('admin-deploy-button');

    let counter = 1;

    // Get the review
    playButton.addEventListener('click', () => {
        fetch('/review')
            .then(response => {
                if (!response.ok) {
                    throw new Error('GET request failed');
                }
                return response.json();
            })
            .then(data => {
                product.innerText = data.product;
                productDescription.innerText = data.product_description;
                review.innerText = data.review;
            })
            .catch(error => {
                console.error(error);
            });
    });

    // Send PUT request
    rateButton.addEventListener('click', () => {
        fetch('/rate', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rating: ratingSlider.value })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('PUT request failed');
            }
            console.log(response.json());
        })
        .catch(error => {
            console.error(error);
        });
    });
    
    ratingSlider.addEventListener('input', () => {
        sliderValue.textContent = ratingSlider.value;
    });
    
    adminCheckButton.addEventListener('click', () => {
        fetch('/admin/check-update')
            .then(response => {
                if (!response.ok) {
                    throw new Error('GET request failed');
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
            })
            .catch(error => {
                console.error(error);
            });
    });
    
    adminDeployButton.addEventListener('click', () => {
        fetch('/admin/deploy-update')
            .then(response => {
                if (!response.ok) {
                    throw new Error('GET request failed');
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
            })
            .catch(error => {
                console.error(error);
            });
    });
    
});
