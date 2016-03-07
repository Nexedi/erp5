portal_catalog = context.portal_catalog

gadget_id_list = context.REQUEST.form.get("gadget_id_list", gadget_id_list)
if not gadget_id_list:
  return None

gadget_id_list = gadget_id_list.split(",")
knowledge_pad = portal_catalog.getResultValue(portal_type="Knowledge Pad",
                                              publication_section_uid=context.getUid(),
                                              validation_state=["visible", "public"],
                                              local_roles="Owner")

for gadget_id in gadget_id_list:
 knowledge_box = knowledge_pad.newContent(portal_type="Knowledge Box")
 gadget_relative_url = "portal_gadgets/%s" % gadget_id
 gadget = portal_catalog.getResultValue(portal_type="Gadget", id=gadget_id)
 if gadget.getValidationState() == "invisible":
  gadget.visible()
 knowledge_box.setSpecialise(gadget_relative_url)
 knowledge_box.visible()
