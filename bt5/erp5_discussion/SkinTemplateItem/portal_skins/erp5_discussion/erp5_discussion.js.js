function clickSaveButtonWithDiscussionPostUidHidden(id, buttonName) {
  /* this will add respective input box for reply post id (so multiple reply buttons can 
     safely coexist in one HTML page with one HTML form.
     Once the button was clicked, the hidden input is removed (so that this can be used
     multiple times without reloading).   
  */
  var hiddenInput = $('<input type="hidden" name="discussion_post_uid">'),
    form = $('form');
  hiddenInput.val(id);
  form.append(hiddenInput);
  clickSaveButton(buttonName);
  hiddenInput.remove();
}

function deleteDiscussionPost(id) {
  clickSaveButtonWithDiscussionPostUidHidden(
    id,
    'DiscussionThread_deleteDiscussionPost'
  );
}

function redirectCreateCitedNewDiscussionPost(id) {
  clickSaveButtonWithDiscussionPostUidHidden(
    id,
    'DiscussionThread_redirectCreateNewDiscussionPost'
  );
}
