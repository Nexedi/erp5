"""
"""
portal = context.getPortalObject()
portal.portal_templates.updateRepositoryBusinessTemplateList(
                              ['http://www.erp5.org/dists/snapshot/bt5/'])
business_template_list = context.Base_getDemoSMBBusinessTemplateList()

kw = {'tag': "start", 'after_method_id': ["immediateReindexObject"]}
for business_template_id in business_template_list:
  portal.portal_templates.activate(**kw).installBusinessTemplatesFromRepositories((business_template_id,))
  kw["after_tag"] = kw["tag"]
  kw["tag"] = business_template_id

return kw
