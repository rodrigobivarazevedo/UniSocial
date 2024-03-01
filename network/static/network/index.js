// Start with first post
let counter = 0;
// Load posts 20 at a time
const quantity = 10;

document.addEventListener('DOMContentLoaded', function() {
    loadPosts();
    // Use buttons to toggle between views
    document.querySelector('#content').addEventListener('keyup', function() {
        var remainingChars = 280 - this.value.length;
        document.querySelector('#characterCount').textContent = remainingChars + ' characters remaining';
    });

    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            alert.remove();
        });
    }, 5000); // 5000 milliseconds = 5 seconds

});


// Event listener for scrolling
window.onscroll = () => {

    // Check if we're at the bottom
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        loadPosts();
    } 

};
 
  
// Load next set of posts
function loadPosts() {
    // Set start and end post numbers, and update counter
    const start = counter;
    const end = start + quantity - 1;
    counter = end + 1;
    // Get new posts and add posts
    fetch(`/posts?start=${start}&end=${end}`)
    .then(response => response.json())
    .then(data => {
        const posts = data.posts; // No need to parse JSON, it's already an object

        // Append the newly loaded posts to the page
        posts.forEach(post => {
            console.log(post.id);
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
                                <p><a href="#" class="likeEmoji" data-postId="${post.id}">&#x2764;</a> ${post.likes_count}</p>
                            </div>

                            <div style="display: inline-block;">
                                <p><a href="#" class="commentEmoji" data-postId="${post.id}">&#x1F4AC;</a> ${post.comments_count}</p>
                            </div>
                            <hr> <!-- Add hr tag here to separate each post -->
                        </div>
                    </div>
                </div>
            `;

            postElement.querySelector('.likeEmoji').addEventListener('click', function(event) {
                // Perform AJAX request to like the post with postId
                // Update the like count on the UI
                alert('Add like for post with ID: ' + post.id);
                const likeCountElement = document.getElementById(`likes_${post.id}`);
                likeCountElement.textContent = parseInt(likeCountElement.textContent) + 1;
              })

            postElement.querySelector('.commentEmoji').addEventListener('click', function(event) {
                // Perform AJAX request or any action related to commenting
                // For demonstration, let's show an alert
                alert('Add comment for post with ID: ' + post.id);
            })
            document.getElementById('posts').appendChild(postElement);
            
        });

    })
    .catch(error => {
        console.error('Error loading more posts:', error);
    });
}

