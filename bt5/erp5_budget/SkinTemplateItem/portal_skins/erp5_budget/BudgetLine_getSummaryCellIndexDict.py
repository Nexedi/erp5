try:
  return container.REQUEST[script.id]
except KeyError:
  pass

dependant_dimensions_dict = context.BudgetLine_getSummaryDimensionKeyDict()

summary_key_dict = {}

from Products.ERP5Type.Utils import cartesianProduct
# also add all cell coordinates in the dictionnary
for cell_key in cartesianProduct(context.getCellRange()):
  for key in cell_key:
    if key in dependant_dimensions_dict:
      summary_key_dict[tuple(cell_key)] = 1
      break

container.REQUEST.set(script.id, summary_key_dict)
return summary_key_dict
