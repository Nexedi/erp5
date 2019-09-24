"""
  Add (if not present) gadgets to current knowledge pad.
"""
active_pad, all_pads = context.ERP5Site_getActiveKnowledgePadForUser(mode, default_pad_group)

active_pad = active_pad.getObject()
gadget_list = active_pad.contentValues(filter={'portal_type': 'Knowledge Box'})
contained_gadgets = [x.getSpecialiseValue().getRelativeUrl() \
                       for x in gadget_list if x.getValidationState() in ('visible', 'invisible',)]
if gadget_relative_url not in contained_gadgets:
  # add only if not there
  knowledge_box = active_pad.newContent(portal_type='Knowledge Box')
  knowledge_box.setSpecialise(gadget_relative_url)
  knowledge_box.visible()
else:
  # reuse gadget
  knowledge_box = [x for x in gadget_list if x.getSpecialiseValue().getRelativeUrl()==gadget_relative_url][0]

context.REQUEST.set('portal_status_message', knowledge_box.getRelativeUrl())
return context.view()
