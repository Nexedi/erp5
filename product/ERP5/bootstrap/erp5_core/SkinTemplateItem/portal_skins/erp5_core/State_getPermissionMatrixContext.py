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


# XXX we need to use a context that is *not* an XML Matrix to override
# methods like this, otherwise attributes can not be accessed
# Unauthorized: You are not allowed to access 'newCell' in this context
# (Your user account is defined outside the context of the object being accessed)
return context.getParentValue().asContext(
    getCell=getCell,
    newCell=newCell,
    hasInRange=hasInRange,
    getWorkflowManagedPermissionList=context.getParentValue().getWorkflowManagedPermissionList,
    getManagedRoleList=context.getManagedRoleList
)
