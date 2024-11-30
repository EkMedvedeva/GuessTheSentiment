document.addEventListener('DOMContentLoaded', async () => {
    
    const reviewImage = document.getElementById('review-image');
    const reviewTitle = document.getElementById('review-title');
    const reviewText = document.getElementById('review-text');
    const reviewSkip = document.getElementById('review-skip');
    const ratingQuestion = document.getElementById('rating-question');
    
    const categoryName = window.location.pathname.split('/')[1];
    const userName = localStorage.getItem('userName');
    
    let reviewIndex = 0;
    let question;
    let reviews;
    
    function reviewUpdate() {
        reviewText.innerText = reviews[reviewIndex].review;
        let split = reviews[reviewIndex].rating.split('/');
        if (split.length == 2) {
            reviewImage.src = `/stars_${split[0]}_${split[1]}.svg`;
        } else {
            reviewImage.removeAttribute('src');
        }
        if (reviews[reviewIndex].title != null) {
            console.log(reviews[reviewIndex].title);
            reviewTitle.innerText = reviews[reviewIndex].title;
            reviewTitle.style.display = 'block';
        } else {
            reviewTitle.style.display = 'none';
        }
    }
    
    try {
        var url = '/reviews?' + new URLSearchParams({
            username: userName,
        }).toString();
        let response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('GET request failed');
        }
        
        const reviewsData = await response.json();
        
        question = reviewsData.question;
        ratingQuestion.innerText = question;
        
        reviews = reviewsData.reviews;
        reviewIndex = 0;
        reviewUpdate();
    } catch (error) {
        console.error(error);
        return;
    }
    
    reviewSkip.addEventListener('click', () => {
        if (reviewIndex < reviews.length - 1) {
            reviewIndex += 1;
        }
        reviewUpdate();
    });
    
});
