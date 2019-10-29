cell_range = []
for i in range(len(context.getMeasureVariationBaseCategoryList())):
  if matrixbox:
    cell_range.append(context.getVariationRangeCategoryItemList(i))
  else:
    cell_range.append([x[0] for x in context.getVariationRangeCategoryItemList(i)])

return cell_range
