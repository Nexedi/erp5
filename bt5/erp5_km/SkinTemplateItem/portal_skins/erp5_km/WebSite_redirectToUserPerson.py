# Example code:
"""
  This scripts tries to redirect to the current user profile

  If user_name is provided as parameter, then it tries to display
  the profile of that user.
"""

translateString = context.Base_translateString

# Return if anonymous
if user_name is None and context.portal_membership.isAnonymousUser():
  msg = translateString("Anonymous users do not have a personal profile.")
  return context.Base_redirect(form_id="view", keep_items={'portal_status_message':msg})

# Call generic erp5_base method to find user value
user_object = context.Base_getUserValueByUserId(user_name)

# Return if no such user
if user_object is None:
  msg = translateString("This user has no personal profile.")
  return context.Base_redirect(form_id="view", keep_items={'portal_status_message':msg})

return user_object.Base_redirect(form_id="view")
