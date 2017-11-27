if lineCallback is None:
  lineCallback = lambda brain, period_name, line_dict: line_dict
if reportCallback is None:
  reportCallback = lambda x: x
by_mirror_section_dict = {}
def myBrainCallback(brain, period_name, line_dict):
  try:
    mirror_section_line_dict = by_mirror_section_dict[line_dict['mirror_section_uid']]
  except KeyError:
    line_dict = lineCallback(brain=brain, period_name=period_name, line_dict=line_dict)
    if line_dict is None:
      return
    by_mirror_section_dict[line_dict['mirror_section_uid']] = line_dict
    return line_dict
  else:
    total_price = line_dict['total_price']
    mirror_section_line_dict[period_name] = mirror_section_line_dict.get(period_name, 0) + total_price
    mirror_section_line_dict['total_price'] = mirror_section_line_dict['total_price'] + total_price
def myReportCallback(line_list):
  return reportCallback(
    sorted(line_list, key=lambda x: x['mirror_section_title']),
  )
return context.AccountingTransactionModule_getAgedBalanceLineList(
  lineCallback=myBrainCallback,
  reportCallback=myReportCallback,
  **kw
)
