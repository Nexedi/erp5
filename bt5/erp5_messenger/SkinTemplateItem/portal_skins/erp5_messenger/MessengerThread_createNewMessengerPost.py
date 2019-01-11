"""
 This script allows to create a new Messenger Post in context.
"""
from DateTime import DateTime
from Products.ERP5Type.Log import log

portal = context.getPortalObject()
person = portal.portal_membership.getAuthenticatedMember().getUserValue()

messenger_thread = context
is_temp_object = messenger_thread.isTempObject()

if is_temp_object:
  # this is a temporary object accessed by its reference
  # we need to get real ZODB one
  messenger_thread = messenger_thread.getOriginalDocument()

# inspired on PostModule_createHTMLPostForSupportRequest
# temporarily using post_module until data structure (and portal_type/module) for Post are defined
post = context.PostModule_createHTMLPostFromText(
  follow_up=follow_up,
  data=text_content,
  source_reference=source_reference,
)

# XXX the UI of support request app should be responsible for generating a unique
# "message id" for each posted message.
if not post.getSourceReference():
  post.setSourceReference(post.getId())
ingest_document_tag = 'ingest-%s' % post.getSourceReference()
after_ingest_document_tag = 'after-ingest-%s' % post.getSourceReference()

document = None
#TODO
#if file not in ("undefined", None):  # XXX "undefined" ? should also be fixed in javascript side
  #get attachment code from PostModule_createHTMLPostForSupportRequest
#else:
  # when we don't upload a document, we can publish the post now.
post.publish()

follow_up_value = portal.restrictedTraverse(follow_up)
assert follow_up_value.getPortalType() == "Messenger Thread"
# TODO: CHECK IF THIS IS NEEDED
# to be able to display the just posted data in MessengerThread_getCommentPostListAsJson,
# we store it in a session variable.
successor_name = successor_link = None
if document is not None:
  successor_link, successor_name = document.getRelativeUrl(), document.getFilename()
portal.portal_sessions[
    '%s.latest_comment' % follow_up_value.getRelativeUrl()]['comment_post_list'] = dict(
    user=post.Base_getOwnerTitle(),
    date=post.getStartDate().ISO8601(),
    text=post.asStrippedHTML(),
    attachment_link=successor_link,
    attachment_name=successor_name,
    message_id=post.getSourceReference(),)

return
