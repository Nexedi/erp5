## Script (Python) "getOrderLineTransformationState"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try:
  modele = context.getDefaultValue('resource',portal_type=['Modele'])
  transformation = modele.modele_transformation()
  result = transformation.portal_workflow.getInfoFor(transformation, 'transform_state')
except:
  result = ''

return result
