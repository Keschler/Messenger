function openModalwithPostContent(postContent, postUser, postDate, postLikes, postRetweets, postCommentsLength, post_id) {
    var modalPostContent = document.querySelector('.modal-post-content');
    modalPostContent.innerHTML = `
        <p class="date">${postDate}</p>
        <p class="user">${postUser}:</p>
        <p class="content">${postContent}</p>
        <div class="post_bar">
            <a class="comment_image"></a>
            <button class="comment">${postCommentsLength}</button>
            <a class="likes_image" href="{{ url_for('likes', post_id=post['_id']) }}"></a>

            <button class="likes">${postLikes}</button>
            <a class="retweet_image" href="{{ url_for('retweet', post_id=post['_id']) }}"></a>
            <button class="retweets">${postRetweets}</button>
        </div>`;
    set_post_id(post_id)
    set_post_creator_username(postUser)
    document.querySelector('.modal').style.display = 'block';
}


function set_post_id(post_id) {
    var hidden_post_id = document.querySelector('#comment_post_id')
    hidden_post_id.value = post_id
}

function set_post_creator_username(postUser){
    var postCreator = document.querySelector('#post_creator')
    postCreator.value = postUser
}