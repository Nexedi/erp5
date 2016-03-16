"""Save the message id of the relative document"""
if document_relative_url:
  document = context.getPortalObject().restrictedTraverse(document_relative_url)
  document.edit(destination_reference=message_id_list[0],
                gateway = gateway_relative_url)
