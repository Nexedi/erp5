from Products.ERP5Type.Message import translateString

return [
  ('', ''),
  (translateString('List of Documents'), 'list'),
  (translateString('Default Export of Each Document'), 'list_view' ),
  (translateString('Default Export of Each Document (One sheet per view)'), 'list_view_separate_sheet'),
]
