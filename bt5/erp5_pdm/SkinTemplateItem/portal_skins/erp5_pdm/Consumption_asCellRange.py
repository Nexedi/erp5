if matrixbox == 1:
  line = [(x[1], x[0]) for x in context.getVariationCategoryItemList()]
else:
  line = context.getVariationCategoryList()

cell_range = [line]
return cell_range
