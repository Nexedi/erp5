"""Returns the name of the owner of current document
"""
owner_id_list = [i[0] for i in context.get_local_roles() if 'Owner' in i[1]]
if owner_id_list:
  from Products.ERP5Security.ERP5UserManager import getUserByLogin
  found_user_list = getUserByLogin(context.getPortalObject(), tuple(owner_id_list))
  if found_user_list:
    return found_user_list[0].getTitle()
  return owner_id_list[0]
