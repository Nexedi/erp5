from DateTime import DateTime
comment_list = context.SupportRequest_getCommentPostList()
if comment_list:
  return DateTime(comment_list[-1]['date'])
