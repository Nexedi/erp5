def Listbox_getListMethodName(self, field):
  """ XXXX"""
  list_method = field.get_value('list_method')
  try:
    list_method_name = getattr(list_method, 'method_name')
  except AttributeError:
    list_method_name = list_method

  return list_method_name

def Field_getSubFieldKeyDict(self, field, id, key=None):
  """XXX"""
  return field.generate_subfield_key(id, key=key)