"""Returns the name of the owner of current document
"""
from zExceptions import Unauthorized
# A single value is generally expecteted, do not bother optimising for other cases unless necessary.
owner_id = None
for user_id, role_set in context.get_local_roles():
  if 'Owner' in role_set:
    owner_id = user_id
    try:
      user = context.Base_getUserValueByUserId(user_id)
      if user is not None:
        return user.getTitle()
    except Unauthorized:
      pass
return owner_id
