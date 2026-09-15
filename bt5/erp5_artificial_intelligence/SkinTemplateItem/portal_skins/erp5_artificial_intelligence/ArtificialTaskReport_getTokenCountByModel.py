"""Answer the token count of this Artificial Task Report, by model.

One run that escalates uses two models. The split of
the token count is one report over the lines. No new stored field holds the
split.

Each line already holds the model. `ArtificialTaskReportLine_processRequest`
writes the token count of the round in the property `quantity`, with the
quantity unit `unit/token`.

The script answers one list of maps. Each map holds the keys `model`,
`line_count` and `token_count`. The list is sorted by the name of the model.

The sum of `token_count` equals `my_total_quantity` of the Artificial Task
only when every line is `stopped` and holds `unit/token`.
WARNING: `my_total_quantity` grows during one run. Compare the two values only
after the state of the Artificial Task is `Responded`.
"""
import json

LINE_PORTAL_TYPE = 'Artificial Task Report Line'

report = context


def getLineModel(report_line):
  """Return the model of one line. Read the property first.

  The property `request_parameter` holds the key `model` too. That key is the
  second source. A line of one older run can hold the key only.
  """
  model_name = report_line.getModel()
  if model_name:
    return model_name
  try:
    parameter_dict = json.loads(report_line.getRequestParameter() or '{}')
  except Exception:
    return 'unknown'
  if not isinstance(parameter_dict, dict):
    return 'unknown'
  return parameter_dict.get('model') or 'unknown'


count_dict = {}
name_list = []
for line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
  model_name = getLineModel(line)
  if model_name not in count_dict:
    count_dict[model_name] = {
      'model': model_name, 'line_count': 0, 'token_count': 0.0}
    name_list.append(model_name)
  row = count_dict[model_name]
  row['line_count'] = row['line_count'] + 1
  row['token_count'] = row['token_count'] + (line.getQuantity() or 0.0)

name_list.sort()
row_list = []
for model_name in name_list:
  row_list.append(count_dict[model_name])
return row_list
