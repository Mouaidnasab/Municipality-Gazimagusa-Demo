// app.js
document.getElementById('addPostButton').addEventListener('click', function() {
    var postForm = document.getElementById('postForm');
    if (postForm.classList.contains('hidden')) {
        postForm.classList.remove('hidden');
        postForm.classList.add('show');
    } else {
        postForm.classList.remove('show');
        postForm.classList.add('hidden');
    }
});
