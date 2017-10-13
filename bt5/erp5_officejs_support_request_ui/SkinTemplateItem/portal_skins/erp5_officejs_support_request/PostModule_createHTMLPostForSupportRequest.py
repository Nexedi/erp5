follow_up_object, = context.getPortalObject().portal_catalog(relative_url=follow_up, limit=1)
follow_up_object.edit()  # update modification date
post = context.PostModule_createHTMLPostFromText(
  follow_up=follow_up,
  data=data,
)

if file != "undefined":  # XXX "undefined" ? should also be fixed in javascript side
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
