## Script (Python) "Coramy_userLabelPrinterDefinition"
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
  'Nicole_Denis' :       'Meto_XS40_2',
  'Christelle_Megret' :  'Meto_XS40_3',
  'Jocelyne_Olejarz' :   'Meto_XS40_4',
  'Nathalie_Wadoux' :    'Meto_XS40_5',
  'Chantal_Hannequin' :  'Meto_XS40_5',
  'Joelle_Gorriez':      'Meto_XS40_6',
  'Gaelle_Manier' :      'Meto_XS40_6'
}

if local_user in printer_dict.keys():
  printer_name = printer_dict[local_user]
else:
  printer_name = 'Meto_XS40_2'

return printer_name
