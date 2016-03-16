field = context.TestResultModule_viewTestPerfResultChartDialog.your_column_list
column_dict = dict((v,k) for k,v in field.get_value('items'))

column_list = context.REQUEST.get('field_' + field.id)
if isinstance(column_list, str):
  column_list = column_list,

return [(x, column_dict[x]) for x in column_list]
