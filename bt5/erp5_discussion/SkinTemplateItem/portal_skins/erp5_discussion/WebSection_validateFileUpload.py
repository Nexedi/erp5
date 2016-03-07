"""
  Use to check if current user is allowed to perform a file upload.
"""
if context.portal_membership.isAnonymousUser() and len(editor.read()) > 1048576 :
  return 0
return 1
