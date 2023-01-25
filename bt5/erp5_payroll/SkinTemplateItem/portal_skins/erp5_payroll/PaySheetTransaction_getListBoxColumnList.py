'''
  this small script return a list of the categories used in the paysheet lines

  parameters :
    - editable :  if editable = 1, the columns returned are editables columns
                  else, all the columns are returned
'''

column_list = []
editable_column_list = [('int_index', 'PaySheet Order'),
                        ('title', 'Title'),]

not_editable_column_list = [('report_section', 'Report Section'),
                            ('source_section_title', 'Service Provider'),
                            ('slice', 'Slice'),]

column_list.extend(editable_column_list)

if not editable:
  column_list.extend(not_editable_column_list)

column_list.append(('base', 'Base'))


# this following columns are add for both edibales and not
for model_line in context.contentValues(portal_type='Pay Sheet Line'):
  for contribution_share in model_line.getContributionShareValueList():
    price = (contribution_share.getId()+'_price', contribution_share.getTitle()+' Share Rate')
    quantity = (contribution_share.getId()+'_total_price',
                contribution_share.getTitle()+' Share Amount')
    if price not in column_list:
      column_list.append(price)
      column_list.append(quantity)

return column_list
