"""
Return a list of values of a given rubric from one or more DSN Records.
Rubrics will be grouped on a given parent's bloc. This bloc must be made unique
by a given rubrique's code.
Values will be returned as a list in a dictionnary, whose keys are the values of
the  unique rubrique's code use to group them.
"""

portal = context.getPortalObject()

if not searched_block:
  searched_block = 'S21.G00.23'

if not grouping_rubric:
  grouping_rubric = 'S21.G00.11.001'

dsn_files = portal.dsn_module.searchFolder(effective_date=">%s" % from_date,
                                           simulation_state='validated',
                                           **kw)

result_dict = {}

for dsn_file in dsn_files:
  # Exclude current and future DSNs
  if dsn_file.getEffectiveDate() >= context.getEffectiveDate():
    continue
  dsn_file = dsn_file.getObject()
  result_dict[dsn_file] = {}
  found_parent = False
  dsn_data = dsn_file.getTextContent()
  is_monthly_dsn = False
  result_bloc = []
  last_rubric = ''
  for line in dsn_data.split('\n'):
    rubric, value = line.split(',', 1)
    value = value.strip('\'')
    # Let's exclude events DSN
    if rubric == 'S20.G00.05.001':
      is_monthly_dsn = (True if value == '01' else False)
    # We found a parent node
    if grouping_rubric == rubric and is_monthly_dsn:
      found_parent = value
      result_dict[dsn_file][value] = []
    # If we have finished a bloc, we add it to the returned dict,
    # and we look for another bloc under the same parent node
    if rubric < last_rubric and found_parent and len(result_bloc):
      result_dict[dsn_file][found_parent].append(result_bloc)
      result_bloc = []
    # The bloc we are looking for has been found. We add it to
    # the corresponding gathering rubric
    if found_parent and searched_block in rubric and is_monthly_dsn:
      result_bloc.append((rubric, value))
      last_rubric = rubric

return result_dict
