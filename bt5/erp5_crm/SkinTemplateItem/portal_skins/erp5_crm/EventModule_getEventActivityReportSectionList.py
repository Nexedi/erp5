from Products.ERP5Form.Report import ReportSection
result = []
selection_columns = [('simulation_state', 'State')]
#Add dynamicaly ticket type columns to the form
#The name of column must be without spaces
for ticket_type in context.getPortalTicketTypeList():
  selection_columns.append((ticket_type.replace(' ',''),ticket_type))
selection_columns.append(('unassigned', 'Unassigned'))
selection_columns.append(('total', 'Total'))

result.append(ReportSection(
              path=context.getPhysicalPath(),
              selection_columns=selection_columns,
              listbox_display_mode='FlatListMode',
              title=context.Base_translateString('Events'),
              form_id='EventModule_viewEventActivityList'))
return result
