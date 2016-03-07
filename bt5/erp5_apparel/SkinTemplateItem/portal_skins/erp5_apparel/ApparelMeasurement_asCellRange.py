if matrixbox == 1:
  line = [ ('measure/'+x[0],x[0]) for x in context.getMeasureItemList()]
else:
  line = [ 'measure/'+x[0] for x in context.getMeasureItemList()]


column = []
tab = []

cell_range = [line]

return cell_range
