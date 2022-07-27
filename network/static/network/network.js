document.addEventListener('DOMContentLoaded', () => {

    // New Post

    // when the form submited add post to db
    const post_form = document.querySelector("#post-form");
    if (post_form) {

        post_form.onsubmit = () => {
        
            // get data from user and fields
            const text = document.querySelector('#post');
            const message = document.querySelector('#message');
            const error_message = document.querySelector('#error');
            const posts_div = document.querySelector('#posts-container');    
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
            // send post request to api to save post

            fetch('/post', {
                method: "POST",
                headers: { 'X-CSRFToken': csrftoken },
                body: JSON.stringify({
                    text: text.value
                })
            })
                .then(response => response.json())
                .then(result => {

                    // if there is error show error message
                    if (result.error !== undefined) {
                        text.className = "form-control is-invalid";
                        error_message.innerHTML = result.error;
                    }

                    // if there is no error show the success message and add post to posts
                    else {

                        // show success message
                        message.innerHTML = result.success;
                        text.className = "form-control";
                        error_message.innerHTML = '';
                        text.value = '';

                        // create new element for the new post and add data to it
                        const new_post = document.createElement('div');
                        new_post.className = "col-6 border mx-auto p-3 fs-5";
                        new_post.innerHTML = `<p class="text-start p-2 b"><a class="fw-bold text-reset a" href="/users/${result.post.poster}">${result.post.poster}</a></p>
                                            <button class="edit-button btn btn-info mb-2 mx-auto" data-post="${result.post.id}">Edit</button>
                                            <p class="text-center text-break">${result.post.text}</p>
                                            <img src="static/network/heart.png" alt="Heart Image" class="me-1"><span>${result.post.likes}</span>
                                            <input type="submit" class="like-button btn btn-primary rounded-pill ms-3" data-like="false" data-pl="${result.post.id}" value="Like">
                                            <p class="fw-lighter text-start ms-3">${result.post.date}</p>`;

                        // add the post to posts
                        posts_div.prepend(new_post); 
                    }
                });
                return false;
            };
    }



    // Follow and Unfollow

    // get follow form
    const follow_form = document.querySelector('#follow-form');

    // when the form is submited send post request to API to update follow 
    if (follow_form) {

        // get the button and form
        const f_button = document.querySelector('#follow-button');
        const error2 = document.querySelector('#error2');
        const followers_div = document.querySelector('#followers');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        follow_form.onsubmit = () => {
            fetch('/follow', {
                method: "POST",
                headers: { 'X-CSRFToken': csrftoken },
                body: JSON.stringify({
                    user_f: f_button.dataset.user,
                    follow: f_button.dataset.follow,
                })
            })
                .then(response => response.json())
                .then(result => {

                    // if there's error display it
                    if (result.error !== undefined) {
                        error2.innerHTML = result.error;
                    }

                    // if the user followed succesfully make button unfollow and update followers number
                    if (result.success === "followed") {
                        f_button.className = "btn btn-danger";
                        f_button.value = "Unfollow";
                        followers_div.innerHTML = `Followers ${result.count}`;
                        f_button.dataset.follow = "true";
                        error2.innerHTML = "";
                    }

                    // if the user unfollowed succesfully make button follow and update followers number
                    if (result.success === "unfollowed") {
                        f_button.className = "btn btn-primary";
                        f_button.value = "Follow";
                        f_button.dataset.follow = "false";
                        followers_div.innerHTML = `Followers ${result.count}`;
                        error2.innerHTML = "";
                    }
                });
            return false;
        };         
    }


    // Edit post

    // get edit button
    const edit_button = document.querySelectorAll('.edit-button');

    // add event listner to edit button
    edit_button.forEach(button => {

        // when button clicked
        button.onclick = () => {

            // hide the edit button
            button.style.display = 'none';
            
            // get post element
            const post_element = button.nextElementSibling;

            // create form and text area and button
            const edit_form = document.createElement('form');
            const edit_textarea = document.createElement('textarea');
            const submit_button = document.createElement('input');

            // modify the textarea and submit button
            edit_textarea.className = "form-control mb-3";
            edit_textarea.value = post_element.innerHTML;
            submit_button.className = "btn btn-primary";
            submit_button.type = "submit";
            submit_button.value = "Save";

            // append button and textarea to form
            edit_form.append(edit_textarea);
            edit_form.append(submit_button);

            // show the form instead of post text
            post_element.innerHTML = "";
            post_element.append(edit_form);

            // add event listener to form
            edit_form.onsubmit = () => {
                
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                // send data to api to edit it
                fetch('/edit_post', {
                    method: "POST",
                    headers: { 'X-CSRFToken': csrftoken },
                    body: JSON.stringify({
                        post: button.dataset.post,
                        text: edit_textarea.value,
                    })
                })
                    .then(response => response.json())
                    .then(result => {

                        var error_element;
                        // if there's error show it
                        if (result.error !== undefined) {

                            // create element to show error
                            error_element = document.createElement('p');
                            error_element.className = "text-danger";
                            error_element.innerHTML = result.error;
                            post_element.append(error_element);
                        }

                        // if there is no error
                        else {
                            
                            // remove error message if there is one
                            if (error_element) {
                                error_element.remove();
                            }

                            // show edited text and edit button
                            post_element.innerHTML = edit_textarea.value;

                            // remove form
                            edit_form.remove();

                            // show edit button
                            button.style.display = 'block';
                        }
                    });
                return false;
            };   
        }
    });
    

    // Like and unlike

    // get all like buttons
    document.querySelectorAll('.like-button').forEach(button => {

        // add event listener for all buttons
        button.onclick = () => {

            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            // post request to API to like or unlike post
            fetch('/like', {
                method: "POST",
                headers: { 'X-CSRFToken': csrftoken },
                body: JSON.stringify({
                    like: button.dataset.like,
                    post: button.dataset.pl,
                })
            })
                .then(response => response.json())
                .then(result => {

                    var like_error;

                    // get likes field
                    const likes = button.previousElementSibling.previousElementSibling;
                    const e = button.nextElementSibling;

                    // if there is error show it
                    if (result.error !== undefined) {
                        like_error = document.createElement('p');
                        like_error.className = "text-danger";
                        like_error.innerHTML = result.error;
                        likes.append(like_error);
                    }

                    // if the user liked succesfully make button unlike and update likes number
                    if (result.success === "liked") {
                        button.className = "like-button btn btn-danger rounded-pill ms-3";
                        button.value = "Unlike";
                        likes.innerHTML = parseInt(likes.innerHTML) + 1;
                        button.dataset.like = "true";
                        
                        // if there is error remove it
                        if (like_error) {
                            like_error.remove();
                        }
                    }

                    // if the user unliked succesfully make button like and update likes number
                    if (result.success === "unliked") {
                        button.className = "like-button btn btn-primary rounded-pill ms-3";
                        button.value = "Like";
                        likes.innerHTML = parseInt(likes.innerHTML) - 1;
                        button.dataset.like = "false";

                        // if there is error remove it
                        if (like_error) {
                            like_error.remove();
                        }
                    }
                });
        }
    });
});
