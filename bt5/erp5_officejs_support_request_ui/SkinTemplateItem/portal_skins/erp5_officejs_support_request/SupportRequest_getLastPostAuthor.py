comment_list = context.SupportRequest_getCommentPostListAsJson(as_json=False)
if comment_list:
  return comment_list[-1]['user']
