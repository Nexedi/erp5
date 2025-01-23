"""
  Return list of attachments for a post.
  We use proxy roles as not in all cases current user is allowed to get attachments but still we need
  to provide a link to them which when used will ask for login.
"""
result = []
for successor in context.getSuccessorValueList():
  result.append({'title': successor.getTitle(),
                 'url': successor.File_getDownloadUrl()})
return result
