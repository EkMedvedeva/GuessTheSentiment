document.addEventListener('DOMContentLoaded', async () => {
    
    let reviewIndex = 0;
    let question;
    let reviews;
    let guessStartTime;
    const categoryName = window.location.pathname.split('/')[1];
    const connection = JSON.parse(sessionStorage.getItem('connection'));
    
    try {
        let url = '/reviews?' + new URLSearchParams({
            connectionHash: connection.hash,
        }).toString();
        let response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('GET request failed');
        }
        
        const reviewsData = await response.json();
        
        question = reviewsData.question;
        reviews = reviewsData.reviews;
    } catch (error) {
        console.error(error);
        return;
    }
    
    const reviewImage = document.getElementById('review-image');
    const reviewTitle = document.getElementById('review-title');
    const reviewText = document.getElementById('review-text');
    const reviewSkip = document.getElementById('review-skip');
    const ratingQuestion = document.getElementById('rating-question');
    const ratingButtons = document.querySelectorAll('#rating-container .button');
    const guessButton = document.getElementById('guess-button');
    
    function ratingButtonsUpdate(selectedButton) {
        ratingButtons.forEach(button => {
            if (selectedButton === null || button !== selectedButton) {
                button.classList.remove('selected');
            }
        });
        if (selectedButton !== null) {
            selectedButton.classList.add('selected');
            guessButton.classList.remove('disabled');
        } else {
            guessButton.classList.add('disabled');
        }
    }
    
    function reviewUpdate() {
        ratingButtonsUpdate(null);
        
        reviewText.innerText = reviews[reviewIndex].review;
        let imageSource = null;
        if (reviews[reviewIndex].hasOwnProperty('rating')) {
            let split = reviews[reviewIndex].rating.split('/');
            imageSource = `/stars_${split[0]}_${split[1]}.svg`;
        } else if (reviews[reviewIndex].hasOwnProperty('recommended')) {
            let recommended = reviews[reviewIndex].recommended;
            if (recommended) {
                imageSource = '/thumb_up.svg';
            } else {
                imageSource = '/thumb_down.svg';
            }
        }
        
        if (imageSource === null) {
            reviewImage.removeAttribute('src');
        } else {
            reviewImage.src = imageSource;
        }
        if (reviews[reviewIndex].title != null) {
            reviewTitle.innerText = reviews[reviewIndex].title;
            reviewTitle.style.display = 'block';
        } else {
            reviewTitle.style.display = 'none';
        }
        guessStartTime = Date.now();
    }
    
    function reviewNavigate() {
        if (reviewIndex < reviews.length - 1) {
            reviewIndex += 1;
            reviewUpdate();
        } else {
            window.location.href = '/thankyou';
        }
    }
    
    reviewSkip.addEventListener('click', () => {
        reviewNavigate();
    });
    
    ratingButtons.forEach(button => {
        button.addEventListener('click', () => {
            ratingButtonsUpdate(button);
        });
    });
    
    guessButton.addEventListener('click', async () => {
        const selectedButton = document.querySelector('#rating-container .button.selected');
        if (selectedButton === null) {
            return;
        }
        const elapsedTime = (Date.now() - guessStartTime) / 1000;
        const rating = selectedButton.getAttribute('data-rating');
        
        try {
            
            let response = await fetch('/review/rate', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    connectionHash: connection.hash,
                    rating: rating,
                    index: reviewIndex,
                    duration: elapsedTime
                })
            });
            
            if (!response.ok) {
                throw new Error('PUT request failed');
            }
            
            const guessData = await response.json();
            
        } catch (error) {
            console.error(error);
        }
        
        reviewNavigate();
    });
    
    ratingQuestion.innerText = question;
    reviewUpdate();
    
});
