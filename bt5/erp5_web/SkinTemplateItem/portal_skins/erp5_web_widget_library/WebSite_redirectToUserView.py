"""
  Search for the current user and redirect to the default view.
  This code is a good example to show how to redirect to
  the appropriate object in the context of a Web Site.

  TODO:
  - Implement a wholistic view on user information
    (documents, membership, etc.)
"""
translateString = context.Base_translateString

# Return if anonymous
if context.portal_membership.isAnonymousUser():
  msg = translateString("Anonymous users do not have a personal profile.")
  return context.Base_redirect(form_id="view",
                               keep_items={'portal_status_message':msg})

# Call generic erp5_base method to find user value
person_object = context.Base_getUserValueByUserId(user)

# Return if no such user
if person_object is None:
  msg = translateString("This user has no personal profile.")
  return context.Base_redirect(form_id="view", keep_items={'portal_status_message':msg})

return person_object.Base_redirect(form_id="view",
                                   keep_items={'editable_mode':editable_mode})
