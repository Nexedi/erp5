## Script (Python) "modele_transformation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
modele = context

# Find a transformation which allows to compute a price
transformation_list = modele.transformation_sql_search(modele_id = modele.getId())

# We search a transformation which state is "fini"
pricing_transformation = None
for transformation in transformation_list:
  transformation = transformation.getObject()
  if transformation is not None:
    if transformation.portal_type == 'Transformation':
      if transformation.getTransformationState() == 'fini':
        pricing_transformation = transformation
        break

return pricing_transformation
