## Script (Python) "Coramy_userPrinterDefinition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=user_name=None
##title=
##
if user_name==None:
  local_user = context.portal_membership.getAuthenticatedMember().getUserName()
else:
  local_user = user_name

printer_dict = {
}

if local_user in printer_dict.keys():
  printer_name = printer_dict[local_user]
else:
  printer_name = 'Xerox_DC_440'

return printer_name
