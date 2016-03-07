"""
  Delete Discussion Post.
"""
discussion_post = getattr(context, delete_discussion_post_id)
discussion_post.reject()
discussion_post.delete()
context.Base_redirect('view', \
                      keep_items={'portal_status_message': context.Base_translateString('Post rejected.')})
