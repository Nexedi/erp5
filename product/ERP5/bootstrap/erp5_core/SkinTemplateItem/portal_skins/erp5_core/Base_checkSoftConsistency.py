from Products.ERP5Type.Core.Workflow import ValidationFailed

try:
  context.Base_checkConsistency(constraint_type_list="soft")
except ValidationFailed as error_list:
  return ". ".join(str(x) for x in error_list.msg)
