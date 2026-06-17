from Products.ERP5Type.Core.Workflow import ValidationFailed

try:
  context.Base_checkConsistency(constraint_type_list="soft")
  return "OK"
except ValidationFailed as error_list:
  return error_list.msg[0]
  #return ", ".join(e for e in error_list)
