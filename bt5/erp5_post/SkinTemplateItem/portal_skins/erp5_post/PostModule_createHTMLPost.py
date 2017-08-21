portal = context.getPortalObject()
now = DateTime()


# create an HTML Post
post_module = portal.post_module
post = post_module.newContent(portal_type='HTML Post')

# get the related object
object_list = portal.portal_catalog(relative_url=follow_up) # with id keyword, this function will return a sequence data type which contains one element.
follow_up_object = None
if object_list:
  follow_up_object = object_list[0].getObject()
else:
  raise LookupError("Target follow up object not found")

follow_up_object.edit(
  modification_date = now
)

post.edit(
  start_date=now,
  follow_up_value=follow_up_object,
  predecessor_value = predecessor if predecessor else None,
  text_content=data,
)

# handle attachments
if file != "undefined":
  document_kw = {'batch_mode': True,
                  'redirect_to_document': False,
                  'file': file}
  document = context.Base_contribute(**document_kw)
  # set relation between post and document
  post.setSuccessorValueList([document])
  # depending on security model this should be changed accordingly
  document.publish()

post.publish()
# We need to reindex the object on server. So the page will get the post which
# just submmitted.
post.immediateReindexObject()

return
