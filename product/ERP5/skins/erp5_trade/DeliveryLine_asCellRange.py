## Script (Python) "DeliveryLine_asCellRange"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
line_ids = context.OrderLine_getMatrixItemlist(base_category_list = ('tax_category', 'coloris', 'variante'), base=1)
column_ids = context.OrderLine_getMatrixItemlist(base_category_list = ('salary_range','taille',), base=1)
tab_ids = context.OrderLine_getMatrixItemlist(base_category_list = ('salary_range','tax_category', 'taille','coloris','variante'),
                                                       base=1, include=0)

line_ids = map(lambda x: x[0], line_ids)
column_ids = map(lambda x: x[0], column_ids)
tab_ids = map(lambda x: x[0], tab_ids)


if len(tab_ids) is 0:
  return [line_ids, column_ids]
elif tab_ids[0] is None:
  return [line_ids, column_ids]
else:
  return [line_ids, column_ids, tab_ids]
