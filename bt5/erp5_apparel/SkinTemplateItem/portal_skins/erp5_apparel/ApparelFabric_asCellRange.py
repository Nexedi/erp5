if matrixbox == 1:
  line = [('composition/'+x.getId(),x.getTranslatedTitleOrId()) for x in context.getCompositionValueList()]
  column = []
  tab = []


else:
  line = [ 'composition/'+x.getId() for x in context.getCompositionValueList()]
  column = []
  tab = []



cell_range = [line, column, tab]

return cell_range
