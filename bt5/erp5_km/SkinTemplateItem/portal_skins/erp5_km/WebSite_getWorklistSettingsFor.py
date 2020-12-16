"""
This script builds a dictionary from the worklist definition.
It includes some copy / paste of code from DCWorkflow. Refactoring
needed through DCWorkflow API extension. 
"""

kw = {}

# Try to access the workflow defined by the action
try:
  workflow_tool = context.portal_workflow
  workflow = getattr(workflow_tool, action['workflow_id'])
except AttributeError:
  return {}

# If this is a worklist action, read the worklist definition
worklist = getattr(workflow.worklists, action['worklist_id'])
for varkey in worklist.getVarMatchKeys():
  kw[varkey] = worklist.getVarMatch(varkey)
  
# Automatically filter workflists per portal type
# so that the same state can be used for different
# worklists and they are not merged
portal_type_list = workflow.getPortalTypeListForWorkflow()
if not portal_type_list:
  return {} # If no portal type uses the workflow, ignore it
if not kw.has_key('portal_type'):
  # Set portal types which use the workflow
  kw['portal_type'] = portal_type_list
    
# Automatically add local role constraint
# XXX TO BE DONE
# Automatically add local role constraint
# etc.

# Return the dictionnary
return kw
