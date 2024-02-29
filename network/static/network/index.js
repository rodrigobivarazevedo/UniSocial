
// Start with first post
let counter = 1;
// Load posts 20 at a time
const quantity = 20;

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
        console.log(data);
        // Access comments directly from data object
        const posts = JSON.parse(data.posts);
        const comments = data.comments; // Already an object list

        // Append the newly loaded posts to the page
        posts.forEach(post => {
            // Create HTML elements for each post and append them to the container
            const postElement = document.createElement('div');
            postElement.innerHTML = `
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-md-8 offset-md-2">
                            <div class="post">
                                <span style="font-size: 1.25rem; font-weight: bold;" class="username">${post.fields.user}</span> <small>(${post.fields.created_at} ago)</small>
                                <p class="mt-2">${post.fields.content}</p>
                            </div>
        
                            <div style="display: inline-block;">
                                <p>&#x2764; ${post.fields.likes_count}</p>
                            </div>
                            <span style="font-size: 0.85rem; font-weight: bold;">Comments</span>
                            ${comments[post.pk] && Array.isArray(comments[post.pk]) ? comments[post.pk].map(comment => `
                                <p>${comment.fields.content}</p>
                                <p>${comment.fields.created_at} ago</p>
                            `).join('') : ''}
                            <hr> <!-- Add hr tag here to separate each post -->
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('posts').appendChild(postElement);
        });
        
        
    })
    .catch(error => {
        console.error('Error loading more posts:', error);
    });
}
  
  