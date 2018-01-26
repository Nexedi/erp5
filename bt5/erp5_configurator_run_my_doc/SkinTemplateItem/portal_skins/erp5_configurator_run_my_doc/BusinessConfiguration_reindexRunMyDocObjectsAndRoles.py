""" This script reindex all the objects created before updating local roles """
portal = context.getPortalObject()
portal.portal_types.recursiveReindexObject()
stack = [
  portal.document_module,
  portal.image_module,
  portal.knowledge_pad_module,
  portal.organisation_module,
  portal.person_module,
  portal.review_module,
  portal.test_page_module,
  portal.web_page_module,
  portal.web_site_module,
]
for obj in stack:
  stack.extend(obj.objectValues())
  obj.updateLocalRolesOnSecurityGroups()
