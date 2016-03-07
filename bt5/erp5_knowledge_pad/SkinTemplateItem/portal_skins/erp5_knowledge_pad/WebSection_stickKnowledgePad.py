knowledge_pad = context.restrictedTraverse(knowledge_pad_url)
knowledge_pad_module = knowledge_pad.getParentValue()

# copy/paste
cp = knowledge_pad_module.manage_copyObjects(ids=[knowledge_pad.getId()])
new_id = context.knowledge_pad_module.manage_pasteObjects(
                                   cb_copy_data=cp)[0]['new_id']
new_knowledge_pad = knowledge_pad_module[new_id]

# set publication section
new_knowledge_pad.setPublicationSectionValue(context)
new_knowledge_pad.visible()

# because workflow state(i.e. visibility is set to default(invisible)
# set manually with respect to original
for original_box in knowledge_pad.objectValues(portal_type="Knowledge Box"):
  destination_box = new_knowledge_pad[original_box.getId()]
  if original_box.getValidationState() == 'visible':
    destination_box.visible()
  elif original_box.getValidationState() == 'deleted':
    destination_box.delete()

return context.Base_redirect(cancel_url, keep_items={
  "portal_status_message": context.Base_translateString('Sticked.')})
