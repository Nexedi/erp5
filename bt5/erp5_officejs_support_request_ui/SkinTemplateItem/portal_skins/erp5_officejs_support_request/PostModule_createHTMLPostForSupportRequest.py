portal = context.getPortalObject()
follow_up_value = portal.restrictedTraverse(follow_up)
assert follow_up_value.getPortalType() == "Support Request"
if not web_site_relative_url:
  web_site_relative_url = context.getWebSiteValue().getRelativeUrl()
web_site = portal.restrictedTraverse(web_site_relative_url)


post = context.PostModule_createHTMLPostFromText(
  follow_up=follow_up,
  data=data,
  source_reference=source_reference,
)

# XXX the UI of support request app should be responsible for generating a unique
# "message id" for each posted message.
if not post.getSourceReference():
  post.setSourceReference(post.getId())
ingest_document_tag = 'ingest-%s' % post.getSourceReference()
after_ingest_document_tag = 'after-ingest-%s' % post.getSourceReference()

document = None
if file not in ("undefined", None):  # XXX "undefined" ? should also be fixed in javascript side
  follow_up_list = []
  project = follow_up_value.getSourceProjectValue()
  if project is not None:
    follow_up_list.append(project.getRelativeUrl())
  group = None
  section = follow_up_value.getDestinationSectionValue()\
      or follow_up_value.getDestinationValue()
  if section is not None:
    group = section.getGroup()
  document_kw = {
    'batch_mode': True,
    'redirect_to_document': False,
    'attach_document_to_context': True,
    'follow_up_list': follow_up_list,
    'group': group,
    'classification': web_site.getLayoutProperty(
        'preferred_attached_document_classification') or\
        portal.portal_preferences.getPreferredDocumentClassification(),
    'file': file,
  }
  with follow_up_value.defaultActivateParameterDict(
      dict(tag=ingest_document_tag), placeless=True):
    # XXX this Base_contribute might update in place another document with same reference
    # and leave the post with a "dead link" for successor value.
    document = follow_up_value.Base_contribute(**document_kw)
  # XXX contribution API should allow to call a method on the final ingested document
  # after ingestion is complete.
  document.activate(
      after_tag=ingest_document_tag,
      tag=after_ingest_document_tag,
  ).Document_afterSupportRequestFilePostIngestion(
      post_relative_url=post.getRelativeUrl(), )
else:
  # when we don't upload a document, we can publish the post now.
  post.publish()

post.activate(
    after_tag=after_ingest_document_tag
# XXX This API is not agreed. Also, we need to consider the possibility
# of ingesting posts through alarm, which is required when we want to ingest
# post without owners (from anoymous users).
).Post_ingestMailMessageForSupportRequest(
    web_site_relative_url=web_site_relative_url)

# to be able to display the just posted data in SupportRequest_getCommentPostListAsJson,
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
