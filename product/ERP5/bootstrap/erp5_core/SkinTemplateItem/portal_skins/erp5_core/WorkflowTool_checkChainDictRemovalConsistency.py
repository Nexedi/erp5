import six
portal = context.getPortalObject()
error_message = []
chain_dict = portal.portal_workflow.getChainDict()
if chain_dict:
  for workflow_id, portal_type_id_list in six.iteritems(chain_dict):
    error_message.append('workflow %s is associated to portal_types %s in chain_dict (portal_workflow) instead of portal_type' % (workflow_id, portal_type_id_list))
  if fixit:
    portal.portal_workflow.reassignWorkflowWithoutConversion()

return error_message
