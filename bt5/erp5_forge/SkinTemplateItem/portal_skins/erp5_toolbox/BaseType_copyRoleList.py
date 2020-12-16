from Products.ERP5Type.Message import translateString
cb_data = context.manage_copyObjects(
     ids=[r.getId() for r in context.contentValues(portal_type='Role Information')])

if portal_type_group_list is not None:
  for ti in context.portal_types.contentValues():
    if ti == context or ti.getId() in portal_type_list:
      continue
    for group in ti.getTypeGroupList():
      if group in portal_type_group_list:
        portal_type_list.append(ti.getId())
        break

for ti in portal_type_list:
  destination_portal_type = context.portal_types[ti]
  if remove_existing_roles:
    destination_portal_type.manage_delObjects(ids=[r.getId() for r in
            destination_portal_type.contentValues(portal_type='Role Information')])

  destination_portal_type.manage_pasteObjects(cb_data)
  if update_local_roles:
    destination_portal_type.updateRoleMapping()

return context.Base_redirect(form_id,
  keep_items=dict(portal_status_message=translateString('Roles copied in ${type_list}',
                          mapping=dict(type_list=', '.join(portal_type_list)))))
