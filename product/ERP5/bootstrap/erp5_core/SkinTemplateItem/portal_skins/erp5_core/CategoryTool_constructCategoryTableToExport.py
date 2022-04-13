editable_property_id_list = ('id', 'title', 'short_title', 'reference',
                             'codification', 'int_index', 'description')

def getHeaderTitle(property_id):
  return ' '.join([s.capitalize() for s in property_id.split('_')])

cat_info_list = []
for base_cat_id in context.REQUEST['category_list']:
  base_cat = context.portal_categories[base_cat_id]
  d = {'base_cat': base_cat}
  d['cat_list'] = cat_list = []
  d['max_cat_depth'] = max_cat_depth = 0
  cat_info_list.append(d)
  temporary_category_list = []
  for cat in context.portal_catalog(portal_type='Category',
                                    sort_on=(('path', 'ascending'),),# This sorting is not enough.
                                    limit=None,
                                    relative_url="%s/%%" % base_cat.getRelativeUrl()):
    cat_relative_url_path_list = cat.getRelativeUrl().split('/')
    cat_depth = len(cat_relative_url_path_list)
    temporary_category_list.append((cat_relative_url_path_list, cat))
    if cat_depth > d['max_cat_depth']:
      d['max_cat_depth'] = cat_depth
  # Sort by split path by Python, if you sort with "/" by MySQL, then the result will be like ('A','A_B/1','A_B/2','A/1','A/2')
  temporary_category_list.sort()
  d['cat_list'] = [i[1] for i in temporary_category_list]

result = []
for cat_info in cat_info_list:
  table_dict = {'name': cat_info['base_cat'].getId()}
  table_dict['row_list'] = row_list = []
  result.append(table_dict)

  # make headers
  header_dict = {}
  table_dict['header_row'] = header_dict

  cat_list = cat_info['cat_list']
  if cat_list:
    max_cat_depth = cat_info['max_cat_depth']
    header_dict['path_cell_list'] = [''] * (max_cat_depth - 1)
    header_dict['path_cell_list'][0] = 'Path'
    header_dict['category_property_list'] = [getHeaderTitle(property_id)
                                             for property_id in editable_property_id_list]
    for cat in cat_list:
      path_cell_list = [''] * (max_cat_depth - 1)
      path_cell_list[len(cat.getRelativeUrl().split('/')) - 2] = '*'
      category_property_list = list(map(cat.getProperty, editable_property_id_list))
      row_list.append({
        'path_cell_list': path_cell_list,
        'category_property_list': category_property_list,
        })
  else:
    header_dict['path_cell_list'] = ['Path']
    header_dict['category_property_list'] = []

return result
#vim: filetype=python
