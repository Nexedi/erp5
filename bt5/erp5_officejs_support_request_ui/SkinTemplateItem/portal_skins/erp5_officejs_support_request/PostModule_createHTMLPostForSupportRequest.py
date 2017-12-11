portal = context.getPortalObject()

# update modification date
if follow_up_uid is not None:
  follow_up_value, = portal.portal_catalog(uid=follow_up_uid, limit=2)
  follow_up_value = follow_up_value.getObject()
elif follow_up is not None:
  follow_up_value, = portal.portal_catalog(relative_url=follow_up, limit=2)
  follow_up_value = follow_up_value.getObject()
follow_up_value.edit()

post = context.PostModule_createHTMLPostFromText(
  text_content=data,
  follow_up_value=follow_up_value,
  predecessor=predecessor,
  **post_edit_kw
)

if file not in ("undefined", None):  # XXX "undefined" ? should also be fixed in javascript side
  document_kw = {'batch_mode': True,
                 'redirect_to_document': False,
                 'file': file}
  document = context.Base_contribute(**document_kw)
  # set relation between post and document
  # XXX successor is used as a way to put a relation between the attachment and the post,
  #     the actual way should be to use a proper container like an Event that will have
  #     one or several posts and one or several attachments.
  post.setSuccessorValueList([document])
  # XXX depending on security model this should be changed accordingly
  document.publish()

def setLastFollowUpRelated(ob, relative_url):
  prefix = "aggregate/"
  category_list = []
  for category in ob.getCategoryList():
    if category.startswith(prefix):
      continue
    category_list.append(category)
  category_list.append(prefix + relative_url)
  ob.setCategoryList(category_list)

post.publish()
# XXX in support request web app interface, discussable page reloads right after
#     adding a post, searching for indexed post + this post (as support request aggregate)
setLastFollowUpRelated(follow_up_value, post.getRelativeUrl())
