from DateTime import DateTime
comment_list = context.SupportRequest_getCommentPostListAsJson(as_json=False)
if comment_list:
  return DateTime(comment_list[-1]['date'])
