if not editor and (
     request.get('field_listbox_title_%s' % request.cell.uid) or
     request.get('field_listbox_reference_%s' % request.cell.uid)):
  return False
return True
