"""
 Install the business template list required to have the demo working.
"""
portal = context.getPortalObject()
portal.portal_templates.updateRepositoryBusinessTemplateList(
                              ['http://www.erp5.org/dists/snapshot/bt5/'])
business_template_list = context.Base_getUngBusinessTemplateList()

kw = dict(tag="start")
for business_template_id in business_template_list:
  if business_template_id not in portal.portal_templates.getInstalledBusinessTemplateTitleList():
    portal.portal_templates.activate(**kw).installBusinessTemplatesFromRepositories((business_template_id,))
    kw["after_tag"] = kw["tag"]
    kw["tag"] = business_template_id

return kw
