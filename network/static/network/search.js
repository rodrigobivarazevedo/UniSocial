document.addEventListener('DOMContentLoaded', function() {
    // Get the search input element
    const searchInput = document.getElementById('search-input');
    const newPostButton = document.getElementById('newPostButton');
    const newPostModal = new bootstrap.Modal(document.getElementById('newPostModal'));
    // Add event listener for keyup event
    searchInput.addEventListener('keyup', async function(event) {
        // Get the search query
        const query = event.target.value;

        // Perform the asynchronous JavaScript call to Django backend
        try {
            const response = await fetch(`/search/users?query=${query}`);
            const data = await response.json();
            
            // Update UI with the response data
            displaySearchResults(data);
        } catch (error) {
            console.error('Error:', error);
        }
    });

    newPostButton.addEventListener('click', function() {
        const newPostModal = new bootstrap.Modal(document.getElementById('newPostModal'));
        newPostModal.show();
    });

    

    // Function to display search results
    function displaySearchResults(data) {
        var searchResultsContainer = document.getElementById('search-results');
        searchResultsContainer.innerHTML = '';  // Clear previous content
        
        // Display users
        data.users.forEach(function(user) {
            var searchResultItem = document.createElement('div');
            var profilePic = document.createElement('img');
            profilePic.src = user.profile_pic ? user.profile_pic : "";  // Set profile picture URL or placeholder image URL
            profilePic.classList.add('img-fluid', 'rounded-circle');  // Add Bootstrap classes for rounded and thumbnail image
            profilePic.style.maxWidth = '50px';  // Set maximum width for the image
            profilePic.style.marginRight = '10px';  // Add margin-right for space between picture and username
            var username = document.createElement('a'); // Changed to anchor tag
            username.href = `/profile/${user.username}/`; // Set the href attribute
            username.textContent = user.username; // Set the text content
            username.classList.add('ml-2'); // Add left margin for space between picture and username
            searchResultItem.appendChild(profilePic);
            searchResultItem.appendChild(username);
            searchResultsContainer.appendChild(searchResultItem);
        });

       // Display hashtags
        data.hashtags.forEach(function(hashtag) {
            var hashtagElement = document.createElement('div'); // Create a div element for each hashtag
            var hashtagLink = document.createElement('a'); // Create an anchor element for the hashtag link
            hashtagLink.textContent = `#${hashtag.name}`; // Set the text content
            hashtagLink.style.fontWeight = 'bold'; // Make the hashtag text bold
            hashtagLink.style.cursor = 'pointer'; // Set cursor to pointer for better UX
            hashtagElement.appendChild(hashtagLink); // Append the hashtag link to the div
            searchResultsContainer.appendChild(hashtagElement); // Append the div to the container

            // Add event listener to the hashtag link
            hashtagLink.addEventListener('click', function(event) {
                event.preventDefault(); // Prevent default link behavior
                var query = hashtag.name; // Get the hashtag name
                // Perform AJAX call
                fetch(`/search/posts?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    // Load search.html page with received data
                    // You may need to adjust this part based on your implementation
                    // For simplicity, assuming the entire page needs to be replaced
                    document.documentElement.innerHTML = data; // Replace entire HTML with search.html content
                })
                .catch(error => {
                    console.error('Error searching posts:', error);
                });
            });
        });


    }

    // Handle form submission inside the modal
    submitPostButton.addEventListener('click', function() {
        const formData = new FormData(document.getElementById('newPostForm'));

        fetch('/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            window.location.reload();  // Reload the page after successful submission
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle errors or display error messages to the user
        });
    });

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
}
});

