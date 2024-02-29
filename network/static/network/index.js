
document.addEventListener('DOMContentLoaded', function() {
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

        // Change color to green
        document.querySelector('body').style.background = 'green';
    } else {

        // Change color to white
        document.querySelector('body').style.background = 'white';
    }

};
 
  
    