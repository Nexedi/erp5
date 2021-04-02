state_permission_role_dict = context.getStatePermissionRolesDict()

def getCell(permission, role, base_id):
  return context.asContext(
      selected=role in state_permission_role_dict.get(permission, ()),
  )

def newCell(permission, role, base_id, portal_type):
  def edit(edit_order, selected=False):
    roles_for_permission = set(
        context.getStatePermissionRolesDict().get(permission, ()))
    if selected:
      roles_for_permission.add(role)
    else:
      roles_for_permission.discard(role)
    context.setPermission(
        permission,
        roles=roles_for_permission,
    )
  return context.asContext(
      edit=edit,
  )

def hasInRange(*args, **kw):
  return True

return context.asContext(
    getCell=getCell,
    newCell=newCell,
    hasInRange=hasInRange,
)
