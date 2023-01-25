'''
  this script get all paysheet lines in the int_index order with all the amounts
  displayed in the lisbox
'''
line_list = context.PaySheetTransaction_getMovementList(sort_on=[('int_index',
                                                                  'ascending')])
def addProperties(line, line_dict, property_list):
  for prop in property_list:
    line_dict[prop] = getattr(line, prop, None)
  return line_dict

line_dict_list = []
property_list = [ 'slice',
                  'base_contribution_list',
                  'base_application_list',
                  'base_name',
                  'base',
                  'employer_price',
                  'employer_quantity',
                  'employee_price',
                  'employee_quantity',
                  'causality',
                ]
for line in line_list:
  if line.getResourceId() == 'total_employee_contributions':
    continue
  line_dict = {
      'group'  : line.getSourceSectionTitle(),
      'source_section_title': line.getSourceSectionTitle(),
      'title'  : line.getTitle(),
      'service' : getattr(line, 'service', None),
      'employer_total_price' : getattr(line, 'employer_total_price', None),
      'employee_total_price' : getattr(line, 'employee_total_price', None),
      }

  addProperties(line=line, line_dict=line_dict, property_list=property_list)

  line_dict_list.append(line_dict)

return line_dict_list
