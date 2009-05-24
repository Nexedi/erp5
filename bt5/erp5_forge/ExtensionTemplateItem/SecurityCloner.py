def cloneSecurity(self, from_id, to_id):
  """
  This methods copies roles from portal_type
  from_id to portal_type to_id
  """
  s = ''
  from_pt = self[from_id]
  to_pt = [self[x] for x in to_id]
  for pt in to_pt:
    pt._roles = ()
    for role in from_pt._roles:
      pt.addRole(
      role.getId(),
      role.Description(),
      role.Title(),
      role.getCondition(),
      '\n'.join(role.getCategory()) or '',
      role.getBaseCategoryScript(),
      ' '.join(role.getBaseCategory()) or '',
      )
    s+='%s\n' % pt
  return s