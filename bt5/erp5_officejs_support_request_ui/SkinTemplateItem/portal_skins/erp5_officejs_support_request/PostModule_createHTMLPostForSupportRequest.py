from Products.ERP5Type.ImmediateReindexContextManager import ImmediateReindexContextManager
follow_up_value = context.getPortalObject().restrictedTraverse(follow_up)
assert follow_up_value.getPortalType() == "Support Request"
follow_up_value.edit()  # update modification date

with ImmediateReindexContextManager() as immediate_reindex_context_manager:
  post = context.PostModule_createHTMLPostFromText(
    follow_up=follow_up,
    data=data,
    immediate_reindex_context_manager=immediate_reindex_context_manager,
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

  post.publish()
