workflow = context.getParentValue()

state_variable = workflow.getStateVariable()
from Products.ERP5Type.Tool.WorkflowTool import SECURITY_PARAMETER_ID
item_list = [(state_variable, state_variable),
             (SECURITY_PARAMETER_ID, SECURITY_PARAMETER_ID)]

for variable in workflow.getVariableValueList():
  if variable.isForCatalog():
    variable_reference = variable.getReference()
    item_list.append((variable_reference, variable_reference))

return item_list
