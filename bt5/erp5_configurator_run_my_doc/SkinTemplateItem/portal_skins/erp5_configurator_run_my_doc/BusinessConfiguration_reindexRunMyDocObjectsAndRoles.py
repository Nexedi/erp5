""" This script reindex all the objects created before updating local roles """
module_list = ['document_module',
               'image_module',
               'knowledge_pad_module',
               'organisation_module',
               'person_module',
               'review_module',
               'test_page_module',
               'web_page_module',
               'web_site_module']

context.portal_types.recursiveImmediateReindexObject()
portal = context.getPortalObject()
for module_id in module_list:
  module = getattr(portal, module_id)
  module.recursiveImmediateReindexObject()
  stack = [module]
  for obj in stack:
    for child in obj.objectValues():
      stack.append(child)
    obj.updateLocalRolesOnSecurityGroups()
    obj.reindexObjectSecurity()
