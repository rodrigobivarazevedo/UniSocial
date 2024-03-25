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
            hashtagLink.addEventListener('click', async function(event) {
                event.preventDefault(); // Prevent default link behavior
                var query = hashtag.name; // Get the hashtag name
                
                // Perform the asynchronous JavaScript call to Django backend
                try {
                    const response = await fetch(`/search/?query=${query}`);
                    const data = await response.json();
                    console.log(data)
                    // Check if the user is on the search.html page
                    if (window.location.pathname === '/search/') {
                        // If the user is already on the search.html page, display search results
                        loadPosts(data);
                    } else {
                        // If the user is not on the search.html page, load the search.html page
                        window.location.href = '/search/';
                        // Wait until the page is loaded
                        await new Promise(resolve => {
                            window.addEventListener('load', resolve);
                        });

                        // After the page is loaded, display search results
                        loadPosts(data);
                        
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });
        });



    }

    // Load next set of posts
    function loadPosts(data) {
        document.getElementById('search_posts').innerHTML = ""; 
        const posts = data.posts; // Extract posts from the data object
    
        // Append the newly loaded posts to the page
        posts.forEach(post => {
            // Create HTML elements for each post and append them to the container
            const postElement = document.createElement('div');
            postElement.innerHTML = `
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-md-8 offset-md-2">
                            <div class="post">
                                <span style="font-size: 1.25rem; font-weight: bold;" class="username"><img src="${post.profile_pic}" class="img-fluid rounded-circle" style="max-width: 50px;" alt="Profile Picture">  <a href="/profile/${post.username}/">${post.username}</a></span> <small>(${post.created_at} ago)</small>
                                <p class="mt-2">${post.content}</p>
                            </div>
    
                            <div style="display: inline-block;">
                                <p><a href="#" class="likeEmoji" id="likes_${post.id}">&#x2764;</a> <span id="likesCount_${post.id}">${post.likes_count}</span></p>
                            </div>
    
                            <div style="display: inline-block;">
                                <p><a href="#" class="commentEmoji" id="comments_${post.id}">&#x1F4AC;</a> <span id="commentsCount_${post.id}">${post.comments_count}</span></p>
                            </div>
    
    
                            <div id="commentsContainer_${post.id}">
                                <!-- Comments will be dynamically added here -->
                            </div>
    
                            <!-- Form to add a comment -->
                            <form id="addCommentForm_${post.id}" style="display: none; padding: 10px; border-radius: 5px; width: 50%;">
                                <textarea id="commentContent_${post.id}" name="commentContent" rows="3" style="width: 100%; margin-bottom: 10px; padding: 5px;" placeholder="Write a comment"></textarea>
                                <button type="submit" style="background-color: #4CAF50; color: white; padding: 5px 15px; border: none; border-radius: 2px; cursor: pointer;">Post Comment</button>
                            </form>
    
                            <hr> <!-- Add hr tag here to separate each post -->
                        </div>
                    </div>
                </div>
            `;
    
            postElement.querySelector('.likeEmoji').addEventListener('click', function(event) {
                // Perform AJAX request to like the post with postId
                event.preventDefault();
                add_like(post.id);
            });
    
            postElement.querySelector('.commentEmoji').addEventListener('click', function(event) {
                // Perform AJAX request or any action related to commenting
                event.preventDefault();
                const commentForm = document.getElementById(`addCommentForm_${post.id}`);
                const commentContainer = document.getElementById(`commentsContainer_${post.id}`);
                commentContainer.style.display = commentContainer.style.display === 'block' ? 'none' : 'block';
                commentForm.style.display = commentForm.style.display === 'block' ? 'none' : 'block';
                load_comments(post.id);
            });
    
            // Attach event listener for the form submission
            postElement.querySelector(`#addCommentForm_${post.id}`).addEventListener('submit', function(event) {
                event.preventDefault(); // Prevent the default form submission
                // Get the comment content from the textarea
                const commentContent = document.getElementById(`commentContent_${post.id}`).value;
                post_comment(post.id, commentContent);
            });
    
            document.getElementById('search_posts').appendChild(postElement); 
        });
    
        // Update the counter only if new posts are loaded
        counter += posts.length;
    }
    

function add_like(post_id) {
    fetch('/posts/likes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Make sure to include CSRF token
        },
        body: JSON.stringify({ post_id: post_id })
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response data here
        if (data.likes_count) {
            // If the response is not null, update the UI with the like count
            updateLikeCount(post_id, data.likes_count);
        }
    })
    .catch(error => console.error('Error:', error)); // Log any unexpected errors to the console
}


function updateLikeCount(post_id, likes_count) {
    // Update the like count in the UI
    const likesCountElement = document.getElementById(`likesCount_${post_id}`);
    if (likesCountElement) {
        likesCountElement.textContent = likes_count;
    }
}


// Function to load comments
function load_comments(post_id){
    fetch(`/posts/comments?post_id=${post_id}`)
    .then(response => response.json())
    .then(data => {
        // Handle the received comments data here
        const commentsContainer = document.getElementById(`commentsContainer_${post_id}`);
        commentsContainer.innerHTML = '';

        data.comments.forEach(comment => {
            const commentElement = document.createElement('div');
            commentElement.innerHTML = `
            <div class="comment mt-2">
                <span style="font-size: 0.75rem; font-weight: bold;" class="username">${comment.user}</span> <small>(${comment.time} ago)</small>
                <p class="mt-2">${comment.content}</p>
            </div>
            `;
            commentsContainer.appendChild(commentElement);
        });
    });
}


// Function to post a comment
function post_comment(post_id, comment_content) {
    // Perform AJAX request to submit the comment
    fetch('/posts/comments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            post_id: post_id,
            comment_content: comment_content
        })
    })
    .then(response => response.json())
    .then(data => {
        // If the comment was added successfully, reload the comments for the post and clear input text
        document.getElementById(`commentContent_${post_id}`).value = '';
        updateCommentCount(post_id, data.comments_count);
        load_comments(post_id);
    })
    .catch(error => console.error('Error:', error));
}


function updateCommentCount(post_id, comments_count) {
    // Update the like count in the UI
    const commentsCountElement = document.getElementById(`commentsCount_${post_id}`);
    if (commentsCountElement) {
        commentsCountElement.textContent = comments_count;
    }
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

