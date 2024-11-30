document.addEventListener('DOMContentLoaded', async () => {
    
    const userNameSpan = document.getElementById('user-name');
    
    let userName;
    let connection = sessionStorage.getItem('connection');
    
    // Create a connection if there is none in the session storage
    if (connection == null) {
        // Send the last username if there is one
        userName = localStorage.getItem('userName');
        requestBody = {}
        if (userName != null) {
            requestBody.username = userName;
        }
        try {
            const response = await fetch('/connection/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error('POST request failed');
            }

            connection = await response.text();
        } catch (error) {
            console.error(error);
            return;
        }
    }
    
    // Update the session and local storage with the received data
    connection = JSON.parse(connection);
    userName = connection.username;
    localStorage.setItem('userName', userName);
    sessionStorage.setItem('connection', JSON.stringify(connection));
    
    if (userName != null) {
        userNameSpan.innerText = userName;
    }
    
});
