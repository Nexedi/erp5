"""
This script builds a dictionary from the worklist definition.
It includes some copy / paste of code from DCWorkflow. Refactoring
needed through DCWorkflow API extension. 
"""

# Try to access the workflow defined by the action
try:
  workflow_tool = context.portal_workflow
  workflow = getattr(workflow_tool, action['workflow_id'])
except AttributeError:
  return {}

# If this is a worklist action, read the worklist definition
worklist = workflow.getWorklistValueByReference(action['worklist_id'])
kw = worklist.getIdentityCriterionDict()

# Automatically filter workflists per portal type
# so that the same state can be used for different
# worklists and they are not merged
portal_type_list = workflow.getPortalTypeListForWorkflow()
if not portal_type_list:
  return {} # If no portal type uses the workflow, ignore it
if 'portal_type' not in kw:
  # Set portal types which use the workflow
  kw['portal_type'] = portal_type_list
    
# Automatically add local role constraint
# XXX TO BE DONE
# Automatically add local role constraint
# etc.

# Return the dictionnary
return kw
