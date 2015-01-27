from Products.ERP5Form.Report import ReportSection
from DateTime import DateTime
params, stat_columns, selection_columns = context.OrderModule_getOrderReportParameterDict()
context.REQUEST.set('stat_columns', stat_columns)
result=[]
result.append(ReportSection(
              path=context.getPhysicalPath(),
              selection_columns=selection_columns,
              listbox_display_mode='FlatListMode',
              selection_params=params,
              form_id='OrderModule_viewOrderStatList'))
return result
