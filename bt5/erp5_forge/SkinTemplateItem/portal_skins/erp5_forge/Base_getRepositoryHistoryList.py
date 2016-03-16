from Products.ERP5VCS.SubversionClient import SubversionSSLTrustError
from Products.ERP5Type.Document import newTempBase

portal = context.getPortalObject()

# For now we will work only under portal_skins
folder_id = context.getParentValue().getId() # replace aq_parent by getParentValue
                                      # once portal_skins is erp5 object

history_list = []
business_template = None
for bt in portal.portal_templates.searchFolder(installation_state='installed'):
  # if installation_state not in catalog, we have to check manually
  if bt.getInstallationState() != 'installed':
    continue
  if folder_id in bt.getTemplateSkinIdList():
    business_template = bt.getObject()

if business_template is not None:
  repository_path = '%s/SkinTemplateItem/portal_skins/%s/%s.xml' % (
    business_template.getTitle(), folder_id, context.getId())

  vcs_tool = business_template.getVcsTool()
  log_list = vcs_tool.log(repository_path, business_template)
  for log_dict in log_list:
    log_dict['message'] = log_dict['message'].replace('\n', '<br/>')
    temp_object = newTempBase(folder=context, id='1', **log_dict)
    history_list.append(temp_object)

return history_list
