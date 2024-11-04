document.addEventListener('DOMContentLoaded', () => {
    
    const reviewImage = document.getElementById('review-image');
    const reviewText = document.getElementById('review-text');
    
    function loadReview() {
        var categoryName = window.location.pathname.split('/')[1];
        var url = '/review?' + new URLSearchParams({
            category: categoryName
        }).toString();
        fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('GET request failed');
            }
            return response.json();
        })
        .then(reviewData => {
            //reviewImage.src = reviewData.image;
            reviewText.innerText = reviewData.review;
        })
        .catch(error => {
            console.error(error);
        });
    }

    loadReview();
    
});
