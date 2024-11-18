document.addEventListener('DOMContentLoaded', async () => {
    
    const userNameSpan = document.getElementById('user-name');
    
    let userName = localStorage.getItem('userName');

    if (userName == null) {
        try {
            const response = await fetch('/user/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    random: true
                })
            });

            if (!response.ok) {
                throw new Error('POST request failed');
            }

            const userData = await response.json();
            localStorage.setItem('userName', userData.username);
            userName = userData.username;
        } catch (error) {
            console.error(error);
            return;
        }
    }

    if (userName != null) {
        userNameSpan.innerText = userName;
    }
    
});
