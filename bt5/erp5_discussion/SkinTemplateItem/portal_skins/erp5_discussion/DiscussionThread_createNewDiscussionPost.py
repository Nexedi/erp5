"""
 This script allows to create a new Discussion Post in context.
"""
from DateTime import DateTime

portal = context.getPortalObject()
person = portal.ERP5Site_getAuthenticatedMemberPersonValue()

discussion_thread = context
is_temp_object = discussion_thread.isTempObject()

if is_temp_object:
  # this is a temporary object accessed by its reference
  # we need to get real ZODB one
  discussion_thread = getattr(discussion_thread.original_container, discussion_thread.original_id)

discussion_post = discussion_thread.newContent(
                    portal_type = "Discussion Post",
                    title = title,
                    text_content = text_content,
                    source_value = person,
                    predecessor_value = predecessor,
                    version = '001',
                    language = portal.Localizer.get_selected_language(),
                    text_format = 'text/html')

# handle attachments
if getattr(file, 'filename', '') != '':
  document_kw = {'batch_mode': True,
                 'redirect_to_document': False,
                 'file': file}
  document = context.Base_contribute(**document_kw)

  # set relation between post and document
  discussion_post.setSuccessorValueList([document])

  # depending on security model this should be changed accordingly
  document.publish()

# depending on security model Post can be submitted for review
portal_status_message = context.Base_translateString("New post created.")

# a parent thread is actually just a logical container so it's modified
# whenever a new post is done
discussion_thread.edit(modification_date = DateTime())

# pass current post's relative url in request so next view
# is able to show it without waiting for indexation
post_relative_url = discussion_post.getRelativeUrl()

if not is_temp_object:
  return discussion_thread.Base_redirect(form_id,
           keep_items = dict(portal_status_message=portal_status_message,
                             post_relative_url = post_relative_url))
else:
  # redirect using again reference
  redirect_url = '%s?portal_status_message=%s&post_relative_url=%s' \
    %(context.REQUEST['URL1'],portal_status_message,post_relative_url)
  context.REQUEST.RESPONSE.redirect(redirect_url)
