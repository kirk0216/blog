const commentsContainer = document.getElementById('comments-container');
const commentsHeader = document.getElementById('comments-header');

const commentBody = document.getElementById('body');
const submitCommentButton = document.getElementById('submit-comment');

submitCommentButton.addEventListener('click', ev => {
    let commentData = new FormData();
    commentData.append('body', commentBody.value);

    fetch(commentURL, { method: 'POST', body: commentData })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                commentsContainer.insertAdjacentHTML('beforeend', result.html);
                commentBody.value = null;

                updateCommentCount();
            }
        })
});

function deleteComment(comment_id) {
    let deleteURL = `/comment/delete/${comment_id}`;

    fetch(deleteURL, { method: 'POST' })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                const commentElement = document.getElementById(`comment-${comment_id}`);
                commentElement.remove();

                updateCommentCount();
            }
        })
}

function updateCommentCount() {
    commentsHeader.innerText = `Comments (${commentsContainer.childElementCount - 1})`;
}
