employee_number_list = []
for career in context.portal_catalog(portal_type='Career',
                                     parent_uid=context.getParentUid()):
  reference = career.getReference()
  if reference and (reference not in employee_number_list):
    employee_number_list.append(reference)
return employee_number_list
