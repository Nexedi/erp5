def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

# result_dict[user][rubric_root][date]
result_dict = {}

change_list = context.objectValues(portal_type="DSN Change Block")

for change in change_list:
  source = change.getSource()
  date = formatDate(change.getReceivedDate())
  rubric = change.getUseValue().getCodification()
  rubric_root = rubric[:-4]
  value = change.getData()

  result_dict.setdefault(source, {}) \
             .setdefault(rubric_root, {}) \
             .setdefault(date, {}) \
             [rubric] = value

return result_dict
