"""
  Print all listbox that uses the same selection name.
"""

selection_name_dict = context.SkinsTool_getDuplicateSelectionNameDict()
for selection_name, field_map in selection_name_dict.items():
  print repr(selection_name), '\n\t', '\n\t'.join(["%r: %s" % (field, skin_list) 
                                                   for field, skin_list in field_map.items()])
return printed
