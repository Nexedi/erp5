from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
follow_up_value = portal.restrictedTraverse(follow_up)
assert follow_up_value.getPortalType() == "Support Request"
if not web_site_relative_url:
  web_site_relative_url = context.getWebSiteValue().getRelativeUrl()
web_site = portal.restrictedTraverse(web_site_relative_url)

# update modification date
portal.portal_workflow.doActionFor(
  follow_up_value,
  'edit_action',
  comment=translateString('New message posted.'))

post = context.PostModule_createHTMLPostFromText(
  follow_up=follow_up,
  data=data,
  source_reference=source_reference,
)

if file not in ("undefined", None):  # XXX "undefined" ? should also be fixed in javascript side
  follow_up_list = []
  project = follow_up_value.getSourceProjectValue()
  if project is not None:
    follow_up_list.append(project.getRelativeUrl())
  group = None
  section = follow_up_value.getSourceSectionValue()
  if section is not None:
    group = section.getGroup()
  document_kw = {
    'batch_mode': True,
    'redirect_to_document': False,
    'follow_up_list': follow_up_list,
    'group': group,
    'classification': web_site.getLayoutProperty(
      'preferred_attached_document_classification') or portal.portal_preferences.getPreferredDocumentClassification(),
    'file': file}
  # XXX this Base_contribute might update in place another document with same reference
  # and leave the post with a "dead link" for successor value.
  document = context.Base_contribute(**document_kw)
  # set relation between post and document
  post.setSuccessorValueList([document])

  document.share()


# XXX the UI of support request app should be responsible for generating a unique
# "message id" for each posted message.
if not post.getSourceReference():
  post.setSourceReference(post.getId())

post.publish()
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
