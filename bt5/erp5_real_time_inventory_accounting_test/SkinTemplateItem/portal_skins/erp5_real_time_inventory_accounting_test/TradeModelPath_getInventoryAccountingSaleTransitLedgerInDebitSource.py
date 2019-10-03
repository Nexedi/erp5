result = []
source_section = movement.getSourceSection()
if source_section:
  result.append('source_section/%s' % source_section)
if movement.getSource() == 'organisation_module/hoge':
  result.append('source/account_module/stock_car_transit')

return result
