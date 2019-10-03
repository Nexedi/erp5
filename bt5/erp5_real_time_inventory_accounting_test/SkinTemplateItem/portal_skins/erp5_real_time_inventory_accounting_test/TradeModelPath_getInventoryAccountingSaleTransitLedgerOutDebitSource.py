result = []
source_section = movement.getSourceSection()
if source_section:
  result.append('source_section/%s' % source_section)
if movement.getSource() == 'organisation_module/hoge':
  result.append('source/account_module/variation_cars')

return result
