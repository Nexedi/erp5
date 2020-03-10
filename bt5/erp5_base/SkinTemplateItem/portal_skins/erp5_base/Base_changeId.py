# this script has an `id` argument
# pylint: disable=redefined-builtin
from Products.ERP5Type.Message import translateString

if id and id != context.getId():
  container = context.getParentValue()

  # rename old one, if existing
  if id in container.objectIds():
    getattr(container, id).setId(container.generateNewId())

  context.setId(id)
  return context.Base_redirect(form_id,
          keep_items=dict(selection_name=selection_name,
                          selection_index=selection_index,
                          portal_status_message=translateString("Function changed.")),)

return context.Base_redirect(form_id,
          keep_items=dict(selection_name=selection_name,
                          selection_index=selection_index,
                          cancel_url=cancel_url,
                          portal_status_message=translateString("Cancelled.")),)
