portal = context.getPortalObject()
ung_website = portal.web_site_module.ung

pad_list = portal.portal_catalog(portal_type="Knowledge Pad",
                                 publication_section_uid=ung_website.getUid())

for pad in pad_list:
  pad_object = context.restrictedTraverse(pad.getPath())
  portal.knowledge_pad_module.deleteContent(pad_object.getId())

person_list = portal.portal_catalog(portal_type="Person",
                                    reference=["ung_user", "ung_user2"])

for person in person_list:
  person_object = context.restrictedTraverse(person.getPath())
  portal.person_module.deleteContent(person_object.getId())

return True
