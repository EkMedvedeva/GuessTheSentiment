document.addEventListener('DOMContentLoaded', async () => {
    
    const reviewImage = document.getElementById('review-image');
    const reviewText = document.getElementById('review-text');
    const reviewSkip = document.getElementById('review-skip');
    
    const categoryName = window.location.pathname.split('/')[1];
    const userName = localStorage.getItem('userName');
    
    let reviewIndex = 0;
    let question;
    let reviews;
    
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
        reviews = reviewsData.reviews;
        reviewText.innerText = reviews[0].review;
        
        console.log(question);
        console.log(reviews);
    } catch (error) {
        console.error(error);
        return;
    }
    
    reviewSkip.addEventListener('click', () => {
        reviewIndex += 1;
        reviewText.innerText = reviews[reviewIndex].review;
    });
    
});
