function deleteDiscussionPost(id){
  /* this will add respective input box for delete post id (so multiple delete buttons can 
     safely coexist in one HTML page with one HTML form */
  $("form").append('<input type="hidden" name="discussion_post_uid" value="' +id +  '">');
  clickSaveButton("DiscussionThread_deleteDiscussionPost");
}

function redirectCreateCitedNewDiscussionPost(id){
  /* this will add respective input box for reply post id (so multiple reply buttons can 
     safely coexist in one HTML page with one HTML form */
  $("form").append('<input type="hidden" name="discussion_post_uid" value="' +id +  '">');
  clickSaveButton("DiscussionThread_redirectCreateNewDiscussionPost");
}

