resolveCategory = context.getPortalObject().portal_categories.resolveCategory
column_item_list = [('title', 'Title'),
                    ('reference', 'Reference'),
                    ('quantity', 'Quantity'),]

cell_range = context.getCellRange(base_id='movement')
if len(cell_range) > 0:
  column_item_list.append(('line_variation_category_list',
                           resolveCategory(cell_range[0][0].split('/')[0]).getTitle()))
if len(cell_range) > 1:
  column_item_list.append(('column_variation_category_list',
                           resolveCategory(cell_range[1][0].split('/')[0]).getTitle()))
if len(cell_range) > 2:
  column_item_list.append(('tab_variation_category_list',
                           resolveCategory(cell_range[2][0].split('/')[0]).getTitle()))

return column_item_list
