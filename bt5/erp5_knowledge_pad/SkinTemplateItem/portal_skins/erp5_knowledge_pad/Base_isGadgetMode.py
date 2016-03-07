"""
  Is it a gadget UI mode?
"""
request = context.REQUEST
list_mode = request.get('list_mode', False)
dialog_mode = request.get('dialog_mode', False)

# in relations "mode" dialog_id is exposed in REQUEST
dialog_id = request.get('dialog_id', None)

if dialog_id is not None or \
  list_mode == True or \
  dialog_mode == True:
  return False

return True
