## Script (Python) "sample_order_line_modele_state"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
modele = context.getDefaultValue('resource',portal_type=['Modele'])

if modele :
 modele_state = modele.portal_workflow.getInfoFor(modele, 'modele_state')
else :
 modele_state = ""

return modele_state
