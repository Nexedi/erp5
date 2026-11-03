"""
Example: if you want to fix print statement under portal_skins/custom, call this script like

context.getPortalObject().portal_skins.custom.Folder_convertPy2ToPy3(
  fixer_suffix_list=['fix_print'],
  filter_method=lambda s: 'print ' in s and 'print(' not in s,
  dry_run=False,
)
"""
for path, e in context.ZopeFind(
  context,
  obj_metatypes=['ERP5 Python Script', 'ERP5 Workflow Script', 'Script (Python)'],
):
  if e.meta_type == 'Script (Python)':
    getter = e.body
    setter = e.write
  else:
    getter = e.getBody
    setter = e.setBody
  source_code = getter()
  if filter_method is not None and not filter_method(source_code):
    print('%s : excluded by filter' % path)
    continue
  new_source_code = context.Base_convertPy2ToPy3(source_code, fixer_suffix_list=fixer_suffix_list)
  if source_code == new_source_code:
    print('%s : no fix is required' % path)
  else:
    if dry_run:
      print('%s : fix is required' % path)
    else:
      print('%s : fixed' % path)
      setter(new_source_code)
return printed
