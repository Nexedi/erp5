comment_list = context.SupportRequest_getCommentPostList()
if comment_list:
  return comment_list[-1]['user']
