if matrixbox == 1:
  column = [  ('apparel_morpho_type/'+x.getId(),x.getTranslatedTitle()) for x in context.getApparelMorphoTypeValueList()]
  line = [ ('size/'+x.getId(),x.getTranslatedTitle()) for x in context.getSizeValueList()]
else:
  column = [  'apparel_morpho_type/'+x.getId() for x in context.getApparelMorphoTypeValueList()]
  line = [ 'size/'+x.getId() for x in context.getSizeValueList()]

tab = []

cell_range = [line, column, tab]

return cell_range
