## Script (Python) "ProductionOrderLine_getResourceState"
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
  return context.portal_workflow.getInfoFor(resource, 'modele_state')
else :
  return ''
