## Script (Python) "Transformation_getAllTransformedResource"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
transformation = context

transformation_list = []
transformation_list.append(transformation)
transformation_list += transformation.getSpecialiseValueList(portal_type='Transformation')

final_t_r_list = []
for my_transformation in transformation_list :
  raw_t_r_list=my_transformation.contentValues(filter={'portal_type':'Transformation Component'})
  transformed_resource_list =my_transformation.sort_object_list(unordered_list=raw_t_r_list, sort_order = (('resource', 'ASC'),) )
  final_t_r_list += transformed_resource_list

return final_t_r_list
