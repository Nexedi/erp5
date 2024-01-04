# Publish all knowledge pad gadgets
for gadget in context.portal_gadgets.objectValues():
  if gadget.getValidationState() == 'invisible':
    gadget.visible()
    gadget.public()

# add to preference a template pad
active_preference = context.portal_preferences.getActivePreference()
knowledge_pad = active_preference.newContent(portal_type="Knowledge Pad",
                                             title="Template Pad")
knowledge_pad.visible()
knowledge_pad.public()


if remove_existing_pads:
  # delete existing pads
  user_knowledge_pad_list = context.ERP5Site_getKnowledgePadListForUser(mode = mode)
  context.knowledge_pad_module.manage_delObjects([x.getId() for x in user_knowledge_pad_list])

print("Done")
return printed
