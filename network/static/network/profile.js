// Start with first post
let counter = 0;
// Load posts 10 at a time
const quantity = 10;

document.addEventListener('DOMContentLoaded', function() {
    loadPosts(userProfileUsername);
    
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            alert.remove();
        });
    }, 5000); // 5000 milliseconds = 5 seconds

    var messageButton = document.querySelector('#messagebutton');
    if (messageButton) {
        messageButton.addEventListener('click', function() {
            // Show the compose modal
            var composeModal = new bootstrap.Modal(document.getElementById('composeModal'));
            composeModal.show();
        });
    }


    // Add event listener for form submission
    document.querySelector('#compose-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const body = document.querySelector('#message').value;
        const csrftoken = getCookie('csrftoken');

        // Send email data to server
        fetch('/mail/emails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken // Include CSRF token in headers
            },
            body: JSON.stringify({
                recipients: userProfileUsername,
                body: body
            })
        })
        .then(response => {
            // Handle response
            if (response.ok) {
                // If the response is successful, do something
                location.reload();
            } else {
                // If the response is not successful, handle the error
                console.error("Failed to send email.");
            }
        })
        .catch(error => {
            // Handle network errors
            console.error('Error:', error);
        });

        // Close the modal after sending the message
        var composeModal = bootstrap.Modal.getInstance(document.getElementById('composeModal'));
        composeModal.hide();
    });

    document.querySelector('#follower-link').addEventListener('click', function(e) {
        e.preventDefault();
        fetch(`/following/${userProfileUsername}?usersfollowers`)
            .then(response => response.json())
            .then(data => {
                var followersModal = new bootstrap.Modal(document.getElementById('followersModal'));
                var modalBody = document.getElementById('followersModal').querySelector('.modal-body');
                modalBody.innerHTML = '';  // Clear previous content
                data.followers.forEach(function(follower) {
                    var followerItem = document.createElement('div');
                    var profilePic = document.createElement('img');
                    profilePic.src = follower.profile_pic ? follower.profile_pic : "";  // Set profile picture URL or placeholder image URL
                    profilePic.classList.add('img-fluid', 'rounded-circle');  // Add Bootstrap classes for rounded and thumbnail image
                    profilePic.style.maxWidth = '100px';  // Set maximum width for the image
                    var username = document.createElement('span');
                    username.textContent = follower.username;
                    followerItem.appendChild(profilePic);
                    followerItem.appendChild(username);
                    modalBody.appendChild(followerItem);
                });
                followersModal.show();
            })
            .catch(error => console.error('Error:', error));
    });
    
    document.querySelector('#following-link').addEventListener('click', function(e) {
        e.preventDefault();
        fetch(`/following/${userProfileUsername}?usersfollowing`)
            .then(response => response.json())
            .then(data => {
                var followingModal = new bootstrap.Modal(document.getElementById('followingModal'));
                var modalBody = document.getElementById('followingModal').querySelector('.modal-body');
                modalBody.innerHTML = '';  // Clear previous content
                data.following_users.forEach(function(followingUser) {
                    var followingItem = document.createElement('div');
                    var profilePic = document.createElement('img');
                    profilePic.src = followingUser.profile_pic ? followingUser.profile_pic : "";  // Set profile picture URL or placeholder image URL
                    profilePic.classList.add('img-fluid', 'rounded-circle');  // Add Bootstrap classes for rounded and thumbnail image
                    profilePic.style.maxWidth = '100px';  // Set maximum width for the image
                    var username = document.createElement('span');
                    username.textContent = followingUser.username;
                    followingItem.appendChild(profilePic);
                    followingItem.appendChild(username);
                    modalBody.appendChild(followingItem);
                });
                followingModal.show();
            })
            .catch(error => console.error('Error:', error));
    });

    

});


// Event listener for scrolling
window.onscroll = () => {
    // Check if we're at the bottom
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        loadPosts(userProfileUsername);
    } 
};
 
  
// Load next set of posts
function loadPosts(userProfileUsername) {
    // Set start and end post numbers, and update counter
    const start = counter;
    const end = start + quantity - 1;
  
    // Get new posts and add posts
    fetch(`/posts?start=${start}&end=${end}&user=${userProfileUsername}`)
    .then(response => response.json())
    .then(data => {
        const posts = data.posts; // No need to parse JSON, it's already an object

        // If no new posts are loaded, don't increase the counter
        if (posts.length === 0) {
            return;
        }

        // Append the newly loaded posts to the page
        posts.forEach(post => {
            // Create HTML elements for each post and append them to the container
            const postElement = document.createElement('div');
            postElement.innerHTML = `
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-md-8 offset-md-2">
                            <div class="post">
                                <span style="font-size: 1.25rem; font-weight: bold;" class="username">${post.username}</span> <small>(${post.created_at} ago)</small>
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
              })

            postElement.querySelector('.commentEmoji').addEventListener('click', function(event) {
                // Perform AJAX request or any action related to commenting
                event.preventDefault();
                const commentForm = document.getElementById(`addCommentForm_${post.id}`);
                const commentContainer = document.getElementById(`commentsContainer_${post.id}`);
                commentContainer.style.display = commentContainer.style.display === 'block' ? 'none' : 'block';
                commentForm.style.display = commentForm.style.display === 'block' ? 'none' : 'block';
                load_comments(post.id);
            })

            // Attach event listener for the form submission
            postElement.querySelector(`#addCommentForm_${post.id}`).addEventListener('submit', function(event) {
                event.preventDefault(); // Prevent the default form submission
                // Get the comment content from the textarea
                const commentContent = document.getElementById(`commentContent_${post.id}`).value;
                post_comment(post.id, commentContent);

            })  
            document.getElementById('posts').appendChild(postElement); 
        });
        // Update the counter only if new posts are loaded
        counter = end + 1;
    })
    .catch(error => {
        console.error('Error loading more posts:', error);
    });

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


