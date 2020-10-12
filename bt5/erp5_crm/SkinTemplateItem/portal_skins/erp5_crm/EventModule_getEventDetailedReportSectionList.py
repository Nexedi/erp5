from Products.ERP5Form.Report import ReportSection
result = []
selection_columns = [('ticket_title', 'Title')]
selection_columns.append(('ticket_type', 'Module'))
selection_columns.append(('resource','Type'))
#Add dynamicaly event states columns to the form
#The name of column must be without spaces
for event_state in context.ERP5Site_getWorkflowStateItemList(
    portal_type=context.getPortalEventTypeList(), state_var='simulation_state', translate=False, display_none_category=False):
  if event_state[1]!='deleted':
    selection_columns.append((event_state[1],event_state[0]))
selection_columns.append(('total', 'Total'))

result.append(ReportSection(
              path=context.getPhysicalPath(),
              selection_columns=selection_columns,
              listbox_display_mode='FlatListMode',
              form_id='EventModule_viewEventDetailedList'))
return result
