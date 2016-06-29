def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

# result_dict[user][rubric_root][date]
result_dict = {}

change_objects = context.searchFolder(portal_type="DSN Change Block")

for change in change_objects:
  source = change.getSourceValue()
  date = formatDate(change.getReceivedDate())
  rubric = change.getUseValue().getCodification()
  rubric_root = rubric[:-4]
  value = change.getData()

  if source not in result_dict:
    result_dict[source] = {}
  if rubric_root not in result_dict[source]:
    result_dict[source][rubric_root] = {}
  if date not in result_dict[source][rubric_root]:
    result_dict[source][rubric_root][date] = {}
  result_dict[source][rubric_root][date][rubric] = value

return result_dict
