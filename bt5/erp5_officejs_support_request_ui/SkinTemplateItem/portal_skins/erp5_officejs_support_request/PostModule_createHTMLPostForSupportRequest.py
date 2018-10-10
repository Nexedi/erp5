from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
follow_up_value = portal.restrictedTraverse(follow_up)
assert follow_up_value.getPortalType() == "Support Request"


post = context.PostModule_createHTMLPostFromText(
  follow_up=follow_up,
  data=data,
  source_reference=source_reference,
)

if file not in ("undefined", None):  # XXX "undefined" ? should also be fixed in javascript side
  document_kw = {'batch_mode': True,
                  'redirect_to_document': False,
                  'file': file}
  # XXX this Base_contribute might update in place another document with same reference
  # and leave the post with a "dead link" for successor value.
  document = context.Base_contribute(**document_kw)
  # set relation between post and document
  # XXX successor is used as a way to put a relation between the attachment and the post,
  #     the actual way should be to use a proper container like an Event that will have
  #     one or several posts and one or several attachments.
  post.setSuccessorValueList([document])
  # XXX depending on security model this should be changed accordingly
  document.publish() # XXX isn't it share a better default ?


# XXX the UI of support request app should be responsible for generating a unique
# "message id" for each posted message.
if not post.getSourceReference():
  post.setSourceReference(post.getId())

if not web_site_relative_url:
  web_site_relative_url = context.getWebSiteValue().getRelativeUrl()

post.publish() # XXX
post.activate().Post_ingestMailMessageForSupportRequest(# XXX This API is not agreed
    web_site_relative_url=web_site_relative_url
)

# to be able to display the just posted data in SupportRequest_getCommentPostListAsJson,
# we store it in a session variable.
successor_list = post.getSuccessorValueList()
successor_name = successor_link = None
if successor_list:
  successor_link, successor_name = successor_list[0].getRelativeUrl(), successor_list[0].getFilename()
portal.portal_sessions[
    '%s.latest_comment' % follow_up_value.getRelativeUrl()]['comment_post_list'] = dict(
    user=post.Base_getOwnerTitle(),
    date=post.getStartDate().ISO8601(),
    text=post.asStrippedHTML(),
    attachment_link=successor_link,
    attachment_name=successor_name,
    message_id=post.getSourceReference(),)
