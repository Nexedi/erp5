from Products.ERP5Form.Report import ReportSection
result=[]
request = context.REQUEST
params = {}

selection_columns = [('validation_state', 'State')]
#Add dynamicaly ticket type columns to the form
#The name of column must be without spaces
for ticket_type in context.getPortalTicketTypeList():
  selection_columns.append((ticket_type.replace(' ',''),ticket_type))
selection_columns.append(('unassigned', 'Unassigned'))
selection_columns.append(('total', 'Total'))

#Future states
params=dict(direction=context.Event_getFutureStateList())
result.append(ReportSection(
              path=context.getPhysicalPath(),
              selection_columns=selection_columns,
              listbox_display_mode='FlatListMode',
              title=context.Base_translateString('Future Events'),
              selection_params=params,
              form_id='EventModule_viewEventActivityList'))

#Past states
params=dict(direction=context.Event_getPastStateList())
result.append(ReportSection(
              path=context.getPhysicalPath(),
              selection_columns=selection_columns,
              listbox_display_mode='FlatListMode',
              title=context.Base_translateString('Past Events'),
              selection_params=params,
              form_id='EventModule_viewEventActivityList'))

return result
