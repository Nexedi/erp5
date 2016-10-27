"""Redirect connected user to his document and anonymous to new document form"""
portal = context.getPortalObject()
member = portal.portal_membership.getAuthenticatedMember()

reference = member.getIdOrUserName()
if reference == "Anonymous User":
  return context.WebSection_viewUploadFileDialog()
else:
  document = context.getDocumentValue(name=reference)
  if document is None:
    message = context.Base_translateString("Sorry, but your file is no more available")
    return context.Base_redirect('WebSection_viewUploadFileDialog', keep_items={'portal_status_message':message})
  return context.Base_redirect('%s/view' % reference)
