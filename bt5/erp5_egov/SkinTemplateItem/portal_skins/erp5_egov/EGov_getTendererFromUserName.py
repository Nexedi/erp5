"""
  Return the tenderer of the procedure 
  ie: return the organisation on wich belong the user
  if it doesn't exist return the user
"""
portal = context.getPortalObject()
user_name = context.getViewPermissionOwner()
user_obj = context.ERP5Site_getPersonObjectFromUserName(user_name)
tenderer = ''
if user_obj is not None:
  organisation_value = user_obj.getCareerSubordinationValue()
  if organisation_value is not None:   
    tenderer = organisation_value.getTitle()
  else:
    tenderer = user_obj.getTitle()
return tenderer
