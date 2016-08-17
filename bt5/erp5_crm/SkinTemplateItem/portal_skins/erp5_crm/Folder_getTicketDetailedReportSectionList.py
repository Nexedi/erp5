from Products.ERP5Form.Report import ReportSection
result=[]
result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Tickets'),
              form_id='Folder_viewTicketStatusList'))

result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Events'),
              form_id='Folder_viewTicketDetailedEventsList'))
return result
