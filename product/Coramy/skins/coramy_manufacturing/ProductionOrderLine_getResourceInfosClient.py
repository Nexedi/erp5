## Script (Python) "ProductionOrderLine_getResourceInfosClient"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try :
  resource = context.getResourceValue()
except :
  resource = None

if resource is not None :
  if context.portal_workflow.getInfoFor(resource, 'modele_state_infos_client') == 'n' :
    return 'Non'
  else :
    return 'Oui'
else :
  return ''
