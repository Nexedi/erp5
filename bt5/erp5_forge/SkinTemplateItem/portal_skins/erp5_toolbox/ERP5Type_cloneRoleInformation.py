"""Obsolete compatibility script.
"""
from erp5.component.module.Log import log
log("Obsolete script, please use BaseType_copyRoleList instead")

print('cloning role information from')
print(from_type)
if to_type_list == ():
  to_type_list = (to_type,)

print("to", to_type_list)

context.portal_types[from_type].BaseType_copyRoleList(remove_existing_roles=True,
                                                      portal_type_list=to_type_list)

return printed
