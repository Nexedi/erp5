"""
This script should be called in following case:
- new business installation after workflow conversion;
- workflow assignement in _chain_by_type with converted workflows' id coming with this new installed bt.
"""

workflow_tool = context.getPortalObject().portal_workflow
type_workflow_dict = workflow_tool.getChainsByType()

for ptype_id in type_workflow_dict:
  ptype = getattr(context.getPortalObject().portal_types, ptype_id, None)
  if ptype is not None:
    for workflow_id in type_workflow_dict[ptype_id]:
      workflow = getattr(workflow_tool, workflow_id, None)
      if workflow and workflow.getPortalType() in ['Workflow', 'Interaction Workflow']:
        # 1. clean DC workflow assignement:
        workflow_tool.delTypeCBT(ptype.id, workflow.id)
        # 2. assign ERP5 Workflow to portal type:
        type_workflow_list = ptype.getTypeWorkflowList()
        if workflow_id not in type_workflow_list:
          ptype.setTypeWorkflowList(ptype.getTypeWorkflowList() + [workflow_id])
