"""
  Print all listbox that uses the same selection name.
"""
import six
selection_name_dict = context.SkinsTool_getDuplicateSelectionNameDict()
for selection_name, field_map in six.iteritems(selection_name_dict):
  print("%s\n\t%s" % (repr(selection_name),
                      '\n\t'.join(["%r: %s" % (field, skin_list)
                                   for field, skin_list in six.iteritems(field_map)])))
return printed
