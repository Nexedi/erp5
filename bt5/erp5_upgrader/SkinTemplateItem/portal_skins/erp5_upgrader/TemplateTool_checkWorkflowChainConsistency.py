import re
template_tool = context

bt5_per_title_dict = {}
bt5_list = [i.getTitle() for i in \
  context.portal_templates.getRepositoryBusinessTemplateList()]

installed_bt5_list = template_tool.getInstalledBusinessTemplateList()
for bt5 in installed_bt5_list:
  bt5_title = bt5.title
  if bt5_title not in bt5_list:
    continue
  bt5_per_title_dict[bt5_title] = bt5

resolved_list = template_tool.resolveBusinessTemplateListDependency(bt5_per_title_dict.iterkeys())

pattern = re.compile(r"(?P<portal_type>.*)[| ]\|[| ](?P<workflow_id>.*)")
portal_type_dict = {}
for _, bt5_id in resolved_list:
  if bt5_id not in bt5_per_title_dict:
    continue
  workflow_chain_list = bt5_per_title_dict[bt5_id].getTemplatePortalTypeWorkflowChainList()
  if not workflow_chain_list:
    continue
  for workflow_chain in workflow_chain_list:
    group_dict = pattern.match(workflow_chain).groupdict()
    portal_type = group_dict['portal_type']
    workflow_id = group_dict['workflow_id']
    workflow_id_list = portal_type_dict.setdefault("%s" % portal_type, [])
    if workflow_id.startswith('-'):
      try:
        workflow_id_list.remove(workflow_id.replace('-', ''))
      except ValueError:
        pass
      continue
    elif workflow_id in workflow_id_list:
      continue
    workflow_id_list.append(workflow_id)

error_list = []
workflow_chain_by_portal_type_dict = context.ERP5Site_dumpWorkflowChainByPortalType()
new_workflow_chain_dict = {'chain_%s' % portal_type : ','.join(chain) \
  for portal_type, chain in workflow_chain_by_portal_type_dict.iteritems()}

for portal_type, workflow_chain in portal_type_dict.iteritems():
  workflow_chain_list = list(workflow_chain_by_portal_type_dict.get(portal_type, []))
  expected_workflow_chain = sorted(workflow_chain)
  if sorted(workflow_chain_list) != expected_workflow_chain:
    error_list.append("%s - Expected: %s <> Found: %s" % (portal_type, ', '.join(workflow_chain), ', '.join(workflow_chain_list)))
    if fixit:
      new_workflow_chain_dict["chain_%s" % portal_type] = ','.join(expected_workflow_chain)

if fixit and new_workflow_chain_dict:
  portal_workflow = context.getPortalObject().portal_workflow
  portal_workflow.manage_changeWorkflows(default_chain="", props=new_workflow_chain_dict)

return error_list
